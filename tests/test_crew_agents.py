"""
Tests CrewAI agent reasoning independently (no platform API calls).
Run: .venv/bin/python -m tests.test_crew_agents
"""
import json
from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process
from agents.agents import product_agent, ceo_agent, engineer_agent_json
from agents.tasks import make_product_task, make_review_task
from crew import _parse_json

IDEA = (
    "melon — open-source privacy-focused voice assistant. "
    "Cross-platform desktop app (Electron) that downloads local transcription models, "
    "records voice, converts speech to text, copies to clipboard."
)


def test_product_agent_generates_spec():
    print("\n=== Test: ProductAgent via CrewAI ===")
    raw = Crew(
        agents=[product_agent],
        tasks=[make_product_task(IDEA, "Define 2-3 personas and 5 prioritised features")],
        process=Process.sequential,
        verbose=True,
    ).kickoff().raw

    print(f"\nRaw output:\n{raw[:300]}...")
    spec = _parse_json(raw)
    print(f"\nParsed spec keys: {list(spec.keys())}")

    assert "value_proposition" in spec
    assert isinstance(spec.get("features"), list)
    print("✓ Product spec generated")
    return spec


def test_ceo_review_loop():
    print("\n=== Test: CEO Review Loop ===")
    spec = test_product_agent_generates_spec()
    spec_str = json.dumps(spec, indent=2)

    raw = Crew(
        agents=[ceo_agent],
        tasks=[make_review_task(spec_str)],
        process=Process.sequential,
        verbose=True,
    ).kickoff().raw

    review = _parse_json(raw)
    print(f"\nReview: {review}")
    assert "verdict" in review
    assert review["verdict"] in ("pass", "fail")
    print(f"✓ CEO review verdict: {review['verdict']}")


if __name__ == "__main__":
    test_ceo_review_loop()
