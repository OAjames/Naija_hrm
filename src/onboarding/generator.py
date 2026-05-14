"""
NairaHR — Onboarding Checklist Generator
Uses Qwen2.5-7B-Instruct to generate a personalised onboarding checklist.
Falls back to a template-based checklist if LLM is unavailable.
"""

from __future__ import annotations
import os
from pathlib import Path

HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"
TEMPLATE_PATH = Path(__file__).parent.parent.parent / "knowledge_base" / "onboarding_templates.md"


class OnboardingGenerator:
    def __init__(self):
        self._hf_client = None
        self._template = self._load_template()

    def _load_template(self) -> str:
        if TEMPLATE_PATH.exists():
            return TEMPLATE_PATH.read_text(encoding="utf-8")
        return ""

    def _llm_client(self):
        if self._hf_client is None:
            from huggingface_hub import InferenceClient
            self._hf_client = InferenceClient(
                model=HF_MODEL,
                token=os.getenv("HF_TOKEN"),
            )
        return self._hf_client

    def generate(
        self,
        name: str,
        role: str,
        department: str = "",
        start_date: str = "",
    ) -> str:
        """
        Generate a personalised onboarding checklist.
        Tries LLM generation first; falls back to template.
        """
        try:
            return self._generate_with_llm(name, role, department, start_date)
        except Exception as e:
            print(f"[Onboarding] LLM failed, using template fallback: {e}")
            return self._generate_from_template(name, role, department, start_date)

    def _generate_with_llm(self, name, role, department, start_date) -> str:
        dept_str = f" in {department}" if department else ""
        date_str = f" starting {start_date}" if start_date else ""

        prompt = f"""You are an HR assistant for a Nigerian company. Generate a detailed onboarding checklist for a new employee.

Employee: {name}
Role: {role}{dept_str}{date_str}

Generate a markdown onboarding checklist with these sections:
1. Documents required from the new hire (include NYSC certificate if applicable, NIN, bank details, pension RSA PIN)
2. Pre-arrival actions for HR
3. Day 1 schedule
4. Week 1 tasks
5. Compliance steps (NSITF registration, PENCOM pension enrolment, PAYE setup, Group Life Insurance)
6. 30-day goals and probation schedule

Make it specific to the {role} role. Use Nigerian HR context. Format as a markdown checklist with [ ] checkboxes.

Checklist:"""

        client = self._llm_client()
        response = client.text_generation(
            prompt,
            max_new_tokens=800,
            temperature=0.4,
        )
        return response.strip()

    def _generate_from_template(self, name, role, department, start_date) -> str:
        """Template-based fallback — always works, no API required."""
        dept_str = f" ({department})" if department else ""
        date_str = f" — Start date: {start_date}" if start_date else ""

        return f"""# Onboarding Checklist — {name}
**Role:** {role}{dept_str}{date_str}

---

## Documents Required from New Hire

- [ ] Signed offer letter / employment contract
- [ ] National Identity Number (NIN) slip or National ID card
- [ ] International Passport (if available)
- [ ] 2 recent passport photographs
- [ ] Academic certificates (WAEC/NECO, B.Sc./HND as applicable)
- [ ] NYSC discharge certificate OR exemption letter *(required for graduates under 30)*
- [ ] Professional certifications relevant to {role} role
- [ ] Bank account details (account number, bank name, account name)
- [ ] Pension RSA PIN (or open new RSA account with a PENCOM-licensed PFA)
- [ ] Tax Identification Number (TIN) — available at FIRS online portal
- [ ] Next of kin details (name, relationship, phone, address)
- [ ] 2 professional reference letters

---

## Pre-Arrival (HR — 1 Week Before Start)

- [ ] Send welcome email with reporting instructions and dress code
- [ ] Set up company email address for {name}
- [ ] Prepare workstation and required equipment
- [ ] Create system accounts (HRMS, email, collaboration tools)
- [ ] Notify IT of new hire and access requirements for {role}
- [ ] Brief line manager and schedule Day 1 welcome meeting
- [ ] Add {name} to relevant team communication channels
- [ ] Add to payroll for current/next cycle

---

## Day 1

- [ ] Welcome tour — office facilities, workstation, exits, kitchen, prayer room
- [ ] Introduction to immediate team members
- [ ] HR meeting: collect all required documents
- [ ] Receive employee handbook and company policies
- [ ] IT setup: laptop, email, system access configured
- [ ] Introduction to HRMS — leave portal, payslip access, policies
- [ ] 1:1 with line manager: role overview and first-week plan
- [ ] Staff ID card or photo session scheduled

---

## Week 1

- [ ] Read and sign: Employee Handbook
- [ ] Read and sign: Code of Conduct
- [ ] Read and sign: Data Protection Policy (NDPA 2023 compliance)
- [ ] Read and sign: IT Acceptable Use Policy
- [ ] Read and sign: Leave Policy (annual: 6+ days; maternity: 12 weeks)
- [ ] Attend company/department induction session
- [ ] Shadow team members to understand workflows
- [ ] Meet cross-functional contacts (Finance, IT, Admin, Compliance)

---

## Statutory Compliance Steps

- [ ] **PENCOM:** Collect RSA PIN; submit to payroll — first pension contribution (18% total) due end of Month 1
- [ ] **NSITF:** HR to register new hire — employer contributes 1% of payroll monthly
- [ ] **PAYE:** Confirm employee's State of Residence for PAYE registration with FIRS
- [ ] **Group Life Insurance:** Add {name} to company policy (minimum 3× annual salary)
- [ ] **ITF:** Update ITF headcount register (if company has 5+ staff)

---

## 30-Day Goals

- [ ] Complete all Week 1 reading and sign-offs
- [ ] Set 90-day performance objectives with line manager (SMART goals)
- [ ] Attend first team meeting / monthly all-hands
- [ ] Probation review scheduled for Day 90
- [ ] Complete any mandatory role-specific training

---

*Generated by NairaHR Agent · Nigerian Labour Act compliant*
"""
