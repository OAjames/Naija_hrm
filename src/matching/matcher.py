"""
NairaHR — Job Matching Module
Scores CV text against a job description using sentence embeddings.
"""

from __future__ import annotations
import re
from typing import Any

# Lazy import for faster cold start
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


# Nigerian HR keywords to boost match awareness
NIGERIAN_REQUIRED_FIELDS = ["nysc", "national youth service", "national youth service corps"]

SKILL_KEYWORDS = [
    "python", "javascript", "java", "sql", "excel", "powerpoint", "react",
    "node.js", "data analysis", "machine learning", "project management",
    "communication", "leadership", "teamwork", "customer service", "sales",
    "marketing", "accounting", "finance", "hr", "recruitment",
]

class JobMatcher:
    def __init__(self):
        self.model = None  # lazy load

    def _embed(self, text: str):
        if self.model is None:
            self.model = _get_model()
        return self.model.encode(text, convert_to_numpy=True)

    def score(self, cv_text: str, job_description: str) -> dict[str, Any]:
        """
        Compare a CV against a job description.

        Returns:
            {
                overall_score: float 0-1,
                skills_score: float 0-1,
                experience_score: float 0-1,
                strengths: list[str],
                gaps: list[str],
                recommendation: str,
                nysc_required: bool,
            }
        """
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        cv_lower = cv_text.lower()
        jd_lower = job_description.lower()

        # ── Overall semantic similarity ────────────────────────────────────
        cv_vec = self._embed(cv_text)
        jd_vec = self._embed(job_description)
        semantic_score = float(cosine_similarity([cv_vec], [jd_vec])[0][0])

        # ── Keyword-level skills match ─────────────────────────────────────
        jd_skills = [kw for kw in SKILL_KEYWORDS if kw in jd_lower]
        cv_skills = [kw for kw in jd_skills if kw in cv_lower]
        skills_score = len(cv_skills) / len(jd_skills) if jd_skills else 0.5

        # ── Weighted overall score ─────────────────────────────────────────
        # semantic: 60%, keyword skills: 40%
        overall_score = (semantic_score * 0.6) + (skills_score * 0.4)
        overall_score = min(max(overall_score, 0.0), 1.0)

        # ── Strengths ──────────────────────────────────────────────────────
        strengths = []
        if cv_skills:
            strengths.append(f"Matched skills: {', '.join(cv_skills[:5])}")
        if any(edu in cv_lower for edu in ["b.sc", "bsc", "bachelor", "master", "msc", "m.sc", "hnd"]):
            strengths.append("Relevant educational qualification found")
        if any(exp in cv_lower for exp in ["years experience", "years of experience", "yr experience"]):
            strengths.append("Work experience section present")
        if any(nysc in cv_lower for nysc in NIGERIAN_REQUIRED_FIELDS):
            strengths.append("NYSC status indicated")
        if semantic_score > 0.7:
            strengths.append("Strong overall alignment with job description")

        # ── Gaps ──────────────────────────────────────────────────────────
        gaps = []
        missing_skills = [kw for kw in jd_skills if kw not in cv_lower]
        if missing_skills:
            gaps.append(f"Skills not evidenced in CV: {', '.join(missing_skills[:4])}")
        nysc_required = any(nysc in jd_lower for nysc in NIGERIAN_REQUIRED_FIELDS)
        if nysc_required and not any(nysc in cv_lower for nysc in NIGERIAN_REQUIRED_FIELDS):
            gaps.append("NYSC discharge/exemption not mentioned — required for this role")
        if overall_score < 0.5:
            gaps.append("Overall alignment with job description is low")

        # ── Recommendation ─────────────────────────────────────────────────
        if overall_score >= 0.75:
            recommendation = "✅ Strong match — recommend for interview."
        elif overall_score >= 0.55:
            recommendation = "🟡 Moderate match — consider for screening interview; address skill gaps."
        else:
            recommendation = "🔴 Weak match — candidate profile significantly differs from job requirements."

        return {
            "overall_score": overall_score,
            "skills_score": skills_score,
            "semantic_score": semantic_score,
            "strengths": strengths if strengths else ["No clear strengths identified from CV text"],
            "gaps": gaps if gaps else ["No critical gaps identified"],
            "recommendation": recommendation,
            "nysc_required": nysc_required,
        }
