"""
NairaHR Agent — Main Gradio Application
Entry point for Hugging Face Spaces deployment.

Tabs:
  1. CV Screening — Upload CV, select job role, get match score
  2. Policy Q&A — Ask any HR policy question
  3. Onboarding — Generate onboarding checklist for a new hire
  4. Dashboard — HR summary view
"""

import os
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

# ── Lazy imports (faster startup) ──────────────────────────────────────────
def get_matcher():
    from src.matching.matcher import JobMatcher
    return JobMatcher()

def get_qa_engine():
    from src.policy_qa.qa_engine import PolicyQAEngine
    return PolicyQAEngine()

def get_onboarding_generator():
    from src.onboarding.generator import OnboardingGenerator
    return OnboardingGenerator()

def get_cv_parser():
    from src.ocr.parser import CVParser
    return CVParser()

# ── Singletons (initialised once) ─────────────────────────────────────────
_matcher = None
_qa_engine = None
_onboarding_gen = None
_cv_parser = None

def matcher():
    global _matcher
    if _matcher is None:
        _matcher = get_matcher()
    return _matcher

def qa_engine():
    global _qa_engine
    if _qa_engine is None:
        _qa_engine = get_qa_engine()
    return _qa_engine

def onboarding_gen():
    global _onboarding_gen
    if _onboarding_gen is None:
        _onboarding_gen = get_onboarding_generator()
    return _onboarding_gen

def cv_parser():
    global _cv_parser
    if _cv_parser is None:
        _cv_parser = get_cv_parser()
    return _cv_parser


# ── Tab 1: CV Screening ────────────────────────────────────────────────────
def screen_cv(cv_file, job_role_text):
    if cv_file is None:
        return "⚠️ Please upload a CV file.", "", "", ""
    if not job_role_text.strip():
        return "⚠️ Please enter or paste a job description.", "", "", ""

    try:
        cv_text = cv_parser().extract(cv_file.name)
        result = matcher().score(cv_text, job_role_text)

        score_display = f"## Match Score: {result['overall_score']:.0%}\n\n"
        strengths = "### ✅ Strengths\n" + "\n".join(f"- {s}" for s in result.get("strengths", []))
        gaps = "### ⚠️ Gaps\n" + "\n".join(f"- {g}" for g in result.get("gaps", []))
        recommendation = f"### 📋 Recommendation\n{result.get('recommendation', '')}"

        return score_display, strengths, gaps, recommendation

    except Exception as e:
        return f"❌ Error processing CV: {str(e)}", "", "", ""


# ── Tab 2: Policy Q&A ──────────────────────────────────────────────────────
def answer_policy_question(question):
    if not question.strip():
        return "Please enter a question."
    try:
        result = qa_engine().answer(question)
        answer = result.get("answer", "I could not find an answer in the knowledge base.")
        source = result.get("source", "")
        escalated = result.get("escalate", False)

        response = answer
        if source:
            response += f"\n\n*Source: {source}*"
        if escalated:
            response += (
                "\n\n---\n"
                "🚨 **This question has been flagged for review by a qualified HR officer.** "
                "Please do not act on this response alone."
            )
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ── Tab 3: Onboarding ──────────────────────────────────────────────────────
def generate_onboarding(name, role, department, start_date):
    if not name.strip() or not role.strip():
        return "⚠️ Please enter the new hire's name and role."
    try:
        checklist = onboarding_gen().generate(
            name=name,
            role=role,
            department=department,
            start_date=start_date,
        )
        return checklist
    except Exception as e:
        return f"❌ Error generating checklist: {str(e)}"


# ── Gradio UI ──────────────────────────────────────────────────────────────
with gr.Blocks(
    title="NairaHR Agent",
    theme=gr.themes.Soft(),
    css="""
        .header { text-align: center; padding: 1rem 0; }
        .flag-badge { color: #b45309; font-weight: 500; }
    """,
) as demo:

    gr.HTML("""
        <div class="header">
            <h1>🇳🇬 NairaHR Agent</h1>
            <p>AI-powered HR assistant for Nigerian SMEs — recruitment, onboarding & compliance</p>
        </div>
    """)

    with gr.Tabs():

        # ── Tab 1 ──────────────────────────────────────────────────────────
        with gr.Tab("📄 CV Screening"):
            gr.Markdown("Upload a candidate CV and paste the job description. The agent will score the match and explain the reasoning.")
            with gr.Row():
                with gr.Column():
                    cv_upload = gr.File(label="Upload CV (PDF)", file_types=[".pdf"])
                    job_desc = gr.Textbox(
                        label="Job Description",
                        placeholder="Paste the full job description here...",
                        lines=8,
                    )
                    screen_btn = gr.Button("🔍 Screen Candidate", variant="primary")
                with gr.Column():
                    score_out = gr.Markdown(label="Score")
                    strengths_out = gr.Markdown(label="Strengths")
                    gaps_out = gr.Markdown(label="Gaps")
                    rec_out = gr.Markdown(label="Recommendation")

            screen_btn.click(
                screen_cv,
                inputs=[cv_upload, job_desc],
                outputs=[score_out, strengths_out, gaps_out, rec_out],
            )

        # ── Tab 2 ──────────────────────────────────────────────────────────
        with gr.Tab("❓ HR Policy Q&A"):
            gr.Markdown("Ask any HR or employment policy question. The agent answers from Nigerian labour law and company policy.")
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. How many days of annual leave am I entitled to?",
                lines=3,
            )
            ask_btn = gr.Button("Ask", variant="primary")
            policy_answer = gr.Markdown(label="Answer")
            ask_btn.click(answer_policy_question, inputs=question_input, outputs=policy_answer)

            gr.Examples(
                examples=[
                    ["What is the minimum wage in Nigeria?"],
                    ["How long is maternity leave?"],
                    ["What pension deductions should appear on my payslip?"],
                    ["What notice period must my employer give before terminating me?"],
                    ["Do I need to provide my NYSC certificate when joining?"],
                ],
                inputs=question_input,
            )

        # ── Tab 3 ──────────────────────────────────────────────────────────
        with gr.Tab("✅ Onboarding Checklist"):
            gr.Markdown("Enter the new hire's details to generate a personalised onboarding checklist with Nigerian compliance steps included.")
            with gr.Row():
                with gr.Column():
                    hire_name = gr.Textbox(label="New Hire Name", placeholder="e.g. Amaka Okonkwo")
                    hire_role = gr.Textbox(label="Role / Job Title", placeholder="e.g. Software Engineer")
                    hire_dept = gr.Textbox(label="Department", placeholder="e.g. Engineering")
                    hire_date = gr.Textbox(label="Start Date", placeholder="e.g. 2 June 2025")
                    onboard_btn = gr.Button("Generate Checklist", variant="primary")
                with gr.Column():
                    checklist_out = gr.Markdown(label="Onboarding Checklist")

            onboard_btn.click(
                generate_onboarding,
                inputs=[hire_name, hire_role, hire_dept, hire_date],
                outputs=checklist_out,
            )

        # ── Tab 4 ──────────────────────────────────────────────────────────
        with gr.Tab("📊 HR Dashboard"):
            gr.Markdown("""
## HR Dashboard

> _In the full version, this tab shows a live summary of candidates screened, questions asked, and onboarding progress. For the hackathon demo, use the other tabs and reference this view as the aggregation layer._

**Planned metrics:**
- Candidates screened this week
- Average match score
- Recurring employee questions (FAQ clusters)
- Onboarding tasks overdue
- Escalation flags pending review
            """)

    gr.HTML("""
        <div style="text-align:center; padding: 1rem; color: #888; font-size: 13px;">
            NairaHR Agent · Built for the Hugging Face AI Hackathon · Nigerian Labour Act compliant
        </div>
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
