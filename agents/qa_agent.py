import os
from crewai import Agent, Task, LLM

_base = dict(
    model=f"ollama/{os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')}",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)
llm_json = LLM(**_base, response_format={"type": "json_object"})

agent = Agent(
    role="QA Reviewer",
    goal="Review landing page HTML and marketing copy against the product spec. Identify gaps and return a structured pass/fail verdict.",
    backstory="Senior QA engineer who is meticulous and never lets vague or inconsistent outputs through.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
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
        agent=agent,
    )
