"""
NairaHR — CV Parser
Extracts text from PDF CVs using PyMuPDF (primary) and Tesseract OCR (fallback).
"""

from __future__ import annotations
import re
from pathlib import Path


class CVParser:
    def extract(self, file_path: str) -> str:
        """
        Extract text from a PDF CV file.
        Tries PyMuPDF first; falls back to Tesseract OCR for scanned PDFs.
        """
        text = self._extract_pymupdf(file_path)
        if len(text.strip()) < 100:
            text = self._extract_tesseract(file_path)
        return text

    @staticmethod
    def _extract_pymupdf(file_path: str) -> str:
        """Extract text layer from a digital PDF."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"[CVParser] PyMuPDF failed: {e}")
            return ""

    @staticmethod
    def _extract_tesseract(file_path: str) -> str:
        """OCR fallback for scanned/image PDFs."""
        try:
            import fitz
            from PIL import Image
            import pytesseract
            import io

            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                text += pytesseract.image_to_string(img)
            doc.close()
            return text
        except Exception as e:
            print(f"[CVParser] Tesseract OCR failed: {e}")
            return "Could not extract text from this PDF. Please upload a text-based PDF."

    @staticmethod
    def parse_fields(cv_text: str) -> dict:
        """
        Extract structured fields from raw CV text.
        Returns a best-effort dict — not all fields will always be found.
        """
        text = cv_text
        fields = {}

        # Email
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            fields["email"] = email_match.group()

        # Phone (Nigerian formats: +234..., 080..., 070..., 081..., etc.)
        phone_match = re.search(r"(\+?234[-\s]?|0)(7|8|9)\d{9}", text)
        if phone_match:
            fields["phone"] = phone_match.group()

        # NYSC mention
        nysc_patterns = ["nysc", "national youth service", "discharge certificate", "exemption certificate"]
        fields["nysc_mentioned"] = any(p in text.lower() for p in nysc_patterns)

        # Education level hints
        education_keywords = {
            "phd": "PhD",
            "m.sc": "MSc",
            "msc": "MSc",
            "master": "Masters",
            "b.sc": "BSc",
            "bsc": "BSc",
            "bachelor": "Bachelors",
            "hnd": "HND",
            "ond": "OND",
            "ssce": "SSCE/WAEC",
            "waec": "SSCE/WAEC",
        }
        found_edu = []
        for key, label in education_keywords.items():
            if key in text.lower():
                found_edu.append(label)
        if found_edu:
            fields["education_levels"] = found_edu

        return fields
