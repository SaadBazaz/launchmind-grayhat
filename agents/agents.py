import os
from crewai import Agent, LLM

_base = dict(
    model=f"ollama/{os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')}",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

# Standard LLM — for free-text tasks (HTML, summaries)
llm = LLM(**_base)

# JSON-mode LLM — forces valid JSON output from Ollama
llm_json = LLM(**_base, response_format={"type": "json_object"})


ceo_agent = Agent(
    role="Startup CEO",
    goal="Orchestrate the team to build and launch a startup. Decompose ideas into tasks, review outputs critically, and drive revision when quality is insufficient.",
    backstory="Serial entrepreneur who has launched 10+ startups. You are decisive, critical, and demand specificity from your team.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
)

product_agent = Agent(
    role="Product Manager",
    goal="Produce detailed, specific product specifications that clearly define personas, features, and user stories for the given startup idea.",
    backstory="Former PM at top tech companies. You write specs that are concrete and actionable, never vague.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
)

engineer_agent = Agent(
    role="Frontend Engineer",
    goal="Generate complete, working HTML landing pages and produce GitHub pull request metadata.",
    backstory="Full-stack engineer who writes clean, self-contained HTML/CSS. You always produce complete files, never stubs.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

engineer_agent_json = Agent(
    role="Frontend Engineer",
    goal="Produce structured JSON metadata for GitHub pull requests and issues.",
    backstory="Full-stack engineer who writes clean structured data for automation pipelines.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
)

marketing_agent = Agent(
    role="Growth Marketer",
    goal="Create compelling marketing copy including taglines, product descriptions, cold emails, and social media posts.",
    backstory="Growth hacker who has driven user acquisition for multiple startups. Your copy is punchy, specific, and always has a clear CTA.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
)

qa_agent = Agent(
    role="QA Reviewer",
    goal="Review landing page HTML and marketing copy against the product spec. Identify gaps and return a structured pass/fail verdict.",
    backstory="Senior QA engineer who is meticulous and never lets vague or inconsistent outputs through.",
    llm=llm_json,
    verbose=True,
    allow_delegation=False,
)
