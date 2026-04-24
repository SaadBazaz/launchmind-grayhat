from crewai import Task
from agents.agents import (
    ceo_agent, product_agent, engineer_agent, engineer_agent_json,
    marketing_agent, qa_agent
)


def make_decompose_task(idea: str) -> Task:
    return Task(
        description=f"""
Decompose this startup idea into a structured task list for your team.
Idea: {idea}

Return ONLY this JSON (no markdown, no explanation):
{{
  "product_task": {{"focus": "one-sentence directive", "context": "relevant detail"}},
  "engineer_task": {{"focus": "one-sentence directive", "context": "relevant detail"}},
  "marketing_task": {{"focus": "one-sentence directive", "context": "relevant detail"}}
}}
""",
        expected_output="JSON object with product_task, engineer_task, marketing_task keys",
        agent=ceo_agent,
    )


def make_product_task(idea: str, focus: str, feedback: str = None) -> Task:
    revision_note = ""
    if feedback:
        revision_note = f"\n\nPREVIOUS OUTPUT REJECTED. Feedback: {feedback}\nRevise to address this feedback specifically."

    return Task(
        description=f"""
Generate a detailed product specification for this startup idea.
Idea: {idea}
Focus: {focus}{revision_note}

Return ONLY this JSON (no markdown, no explanation):
{{
  "value_proposition": "one sentence — what it does and for whom",
  "personas": [
    {{"name": "string", "role": "string", "pain_point": "specific, quantified pain"}}
  ],
  "features": [
    {{"name": "string", "description": "string", "priority": 1}}
  ],
  "user_stories": [
    {{"as_a": "string", "i_want": "string", "so_that": "string"}}
  ]
}}

Requirements: 2-3 personas, exactly 5 features ranked 1-5, exactly 3 user stories.
""",
        expected_output="JSON product specification",
        agent=product_agent,
    )


def make_review_task(spec_json: str) -> Task:
    return Task(
        description=f"""
Review this product specification critically.
Spec: {spec_json}

Check: Are personas specific with real pain points? Are features concrete and distinct? Are user stories actionable?

Return ONLY this JSON (no markdown):
{{
  "verdict": "pass" or "fail",
  "reason": "one sentence",
  "feedback": "specific revision instructions if fail, else null"
}}
""",
        expected_output="JSON review verdict with verdict, reason, feedback fields",
        agent=ceo_agent,
    )


def make_html_task(spec_json: str) -> Task:
    return Task(
        description=f"""
Generate a complete, self-contained HTML landing page for this product.
Spec: {spec_json}

Include: product name as headline, value proposition as subheadline, all 5 features listed with descriptions, a CTA button ("Get Early Access"), and clean inline CSS with a modern color scheme.

Return ONLY raw HTML — no markdown, no code fences, no explanation. Start with <!DOCTYPE html>.
""",
        expected_output="Complete HTML document starting with <!DOCTYPE html>",
        agent=engineer_agent,
    )


def make_pr_meta_task(spec_json: str) -> Task:
    return Task(
        description=f"""
Write GitHub pull request metadata for a landing page commit.
Product spec: {spec_json}

Return ONLY this JSON (no markdown):
{{
  "title": "PR title under 72 chars",
  "body": "markdown PR description, 3-5 sentences explaining what was built and why"
}}
""",
        expected_output="JSON with title and body fields",
        agent=engineer_agent_json,
    )


def make_marketing_task(spec_json: str) -> Task:
    return Task(
        description=f"""
Generate all marketing copy for this product launch.
Spec: {spec_json}

Return ONLY this JSON (no markdown):
{{
  "tagline": "under 10 words",
  "landing_description": "2-3 sentence product description",
  "cold_email": {{
    "subject": "email subject line",
    "body": "150-200 word cold outreach email with clear CTA"
  }},
  "social_posts": {{
    "twitter": "under 280 chars with hashtags",
    "linkedin": "professional tone, 2-3 sentences",
    "instagram": "casual tone with emoji and hashtags"
  }}
}}
""",
        expected_output="JSON marketing copy object",
        agent=marketing_agent,
    )


def make_qa_task(spec_json: str, html: str, copy_json: str) -> Task:
    return Task(
        description=f"""
Review the landing page HTML and marketing copy against the product spec.

Spec: {spec_json}

HTML (first 1500 chars): {html[:1500]}

Marketing copy: {copy_json}

Check HTML: does headline match value_proposition? Are all 5 features present? Is there a CTA?
Check copy: is tagline under 10 words? Does cold email have a CTA? Is tone appropriate?

Return ONLY this JSON (no markdown):
{{
  "overall_verdict": "pass" or "fail",
  "html_review": {{"verdict": "pass" or "fail", "issues": ["issue1", "issue2"]}},
  "copy_review": {{"verdict": "pass" or "fail", "issues": ["issue1"]}},
  "pr_comments": ["comment for PR review 1", "comment for PR review 2"]
}}
""",
        expected_output="JSON QA review report",
        agent=qa_agent,
    )


def make_final_summary_task(spec_json: str, pr_url: str, qa_verdict: str) -> Task:
    return Task(
        description=f"""
Write a concise Slack launch announcement for your team.
Product spec: {spec_json}
GitHub PR: {pr_url}
QA verdict: {qa_verdict}

Write 3-4 sentences summarising what was built, the value proposition, and next steps.
Return plain text only — no JSON, no markdown headers.
""",
        expected_output="Plain text Slack announcement, 3-4 sentences",
        agent=ceo_agent,
    )
