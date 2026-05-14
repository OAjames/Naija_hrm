"""
NairaHR — Policy Q&A Engine
RAG pipeline: ChromaDB retrieval + Qwen2.5 generation.
"""

from __future__ import annotations
import os
import glob
from pathlib import Path
from typing import Any

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent / "knowledge_base"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
ESCALATION_THRESHOLD = float(os.getenv("ESCALATION_THRESHOLD", "0.6"))
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# Sensitive topics that always trigger escalation
ESCALATION_KEYWORDS = [
    "dismissed", "dismissal", "fired", "terminate", "termination",
    "discrimination", "harass", "harassment", "assault", "abuse",
    "pregnant", "pregnancy", "religion", "tribe", "ethnic",
    "legal action", "lawsuit", "sue", "court",
]


class PolicyQAEngine:
    def __init__(self):
        self._collection = None
        self._hf_client = None
        self._setup()

    def _setup(self):
        """Load knowledge base into ChromaDB."""
        import chromadb
        from chromadb.utils import embedding_functions

        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self._collection = client.get_or_create_collection(
            name="nairahr_kb",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        # Only index if collection is empty
        if self._collection.count() == 0:
            self._index_knowledge_base()

    def _index_knowledge_base(self):
        """Chunk and index all markdown files in the knowledge base."""
        md_files = glob.glob(str(KNOWLEDGE_BASE_DIR / "**/*.md"), recursive=True)
        docs, ids, metadatas = [], [], []

        for fpath in md_files:
            source = Path(fpath).name
            text = Path(fpath).read_text(encoding="utf-8")
            chunks = self._chunk_text(text, chunk_size=500, overlap=50)
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                ids.append(f"{source}_{i}")
                metadatas.append({"source": source, "file": fpath})

        if docs:
            self._collection.add(documents=docs, ids=ids, metadatas=metadatas)
            print(f"[PolicyQA] Indexed {len(docs)} chunks from {len(md_files)} files.")

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Split text into overlapping word-count chunks."""
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        return chunks

    def _llm_generate(self, prompt: str) -> str:
        """Call Qwen2.5 via HF Inference API."""
        if self._hf_client is None:
            from huggingface_hub import InferenceClient
            self._hf_client = InferenceClient(
                model=HF_MODEL,
                token=os.getenv("HF_TOKEN"),
            )
        response = self._hf_client.text_generation(
            prompt,
            max_new_tokens=400,
            temperature=0.3,
            stop_sequences=["</answer>", "\n\n\n"],
        )
        return response.strip()

    def answer(self, question: str) -> dict[str, Any]:
        """
        Answer an HR policy question using RAG.

        Returns:
            {answer: str, source: str, escalate: bool, confidence: float}
        """
        # ── Escalation check ───────────────────────────────────────────────
        q_lower = question.lower()
        should_escalate = any(kw in q_lower for kw in ESCALATION_KEYWORDS)

        # ── Retrieve relevant chunks ───────────────────────────────────────
        results = self._collection.query(
            query_texts=[question],
            n_results=3,
            include=["documents", "distances", "metadatas"],
        )

        retrieved_docs = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        # ChromaDB cosine distance: 0 = identical, 2 = opposite
        # Convert to confidence: 1 - (distance/2)
        confidence = 1 - (distances[0] / 2) if distances else 0.0

        if confidence < ESCALATION_THRESHOLD:
            should_escalate = True

        # ── Source citation ────────────────────────────────────────────────
        sources = list({m.get("source", "HR Knowledge Base") for m in metadatas})
        source_str = ", ".join(sources[:2])

        # ── Build RAG prompt ───────────────────────────────────────────────
        context = "\n\n---\n\n".join(retrieved_docs)
        prompt = f"""You are a helpful Nigerian HR policy assistant. Answer the employee's question based ONLY on the context provided. Be concise and specific. If the context does not contain enough information, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

        try:
            answer = self._llm_generate(prompt)
        except Exception as e:
            answer = (
                "I was unable to retrieve an answer from the knowledge base at this time. "
                "Please contact your HR officer directly."
            )
            should_escalate = True

        return {
            "answer": answer,
            "source": source_str,
            "escalate": should_escalate,
            "confidence": confidence,
        }
