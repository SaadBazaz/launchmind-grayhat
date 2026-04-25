import os
from crewai import Agent, Task, LLM

_base = dict(
    model=f"ollama/{os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')}",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)
llm = LLM(**_base)
llm_json = LLM(**_base, response_format={"type": "json_object"})

# Free-text agent for HTML generation
agent = Agent(
    role="Frontend Engineer",
    goal="Generate complete, working HTML landing pages and produce GitHub pull request metadata.",
    backstory="Full-stack engineer who writes clean, self-contained HTML/CSS. You always produce complete files, never stubs.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# JSON-mode variant for structured metadata tasks
agent_json = Agent(
    role="Frontend Engineer",
    goal="Produce structured JSON metadata for GitHub pull requests and issues.",
    backstory="Full-stack engineer who writes clean structured data for automation pipelines.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
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
        agent=agent,
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
        agent=agent_json,
    )
