import os
from crewai import Agent, Task, LLM

_base = dict(
    model=f"ollama/{os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')}",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)
llm_json = LLM(**_base, response_format={"type": "json_object"})

agent = Agent(
    role="Growth Marketer",
    goal="Create compelling marketing copy including taglines, product descriptions, cold emails, and social media posts.",
    backstory="Growth hacker who has driven user acquisition for multiple startups. Your copy is punchy, specific, and always has a clear CTA.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
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
        agent=agent,
    )
