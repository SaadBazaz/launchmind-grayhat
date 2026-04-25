import os
from crewai import Agent, Task, LLM

_base = dict(
    model=f"ollama/{os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')}",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)
llm_json = LLM(**_base, response_format={"type": "json_object"})

agent = Agent(
    role="Product Manager",
    goal="Produce detailed, specific product specifications that clearly define personas, features, and user stories for the given startup idea.",
    backstory="Former PM at top tech companies. You write specs that are concrete and actionable, never vague.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
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
        agent=agent,
    )
