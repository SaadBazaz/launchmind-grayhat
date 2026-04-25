import os
from crewai import Agent, Task, LLM

_base = dict(
    model=f"ollama/{os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')}",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)
llm_json = LLM(**_base, response_format={"type": "json_object"})
llm = LLM(**_base)

agent = Agent(
    role="Startup CEO",
    goal="Orchestrate the team to build and launch a startup. Decompose ideas into tasks, review outputs critically, and drive revision when quality is insufficient.",
    backstory="Serial entrepreneur who has launched 10+ startups. You are decisive, critical, and demand specificity from your team.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
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
        agent=agent,
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
        agent=agent,
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
        agent=agent,
    )
