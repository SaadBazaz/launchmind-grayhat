"""
Independent test for ProductAgent.
Run: .venv/bin/python -m tests.test_product_agent
"""
import json
from agents.product_agent import ProductAgent


def test_product_agent():
    agent = ProductAgent()

    task = {
        "idea": "A mobile app that connects students with local tutors",
        "focus": "Define core user personas and top 5 features",
    }

    print("\n=== ProductAgent Test ===")
    print(f"Input idea: {task['idea']}")
    spec = agent.run(task)

    print("\n--- Output ---")
    print(json.dumps(spec, indent=2))

    # Assertions
    assert "value_proposition" in spec, "Missing value_proposition"
    assert isinstance(spec["personas"], list), "personas must be list"
    assert len(spec["personas"]) >= 2, "Need at least 2 personas"
    assert isinstance(spec["features"], list), "features must be list"
    assert len(spec["features"]) == 5, f"Need exactly 5 features, got {len(spec['features'])}"
    assert isinstance(spec["user_stories"], list), "user_stories must be list"
    assert len(spec["user_stories"]) == 3, f"Need exactly 3 user stories, got {len(spec['user_stories'])}"

    print("\n✓ All assertions passed")

    # Test revision path
    print("\n=== Revision Test (with feedback) ===")
    spec2 = agent.run(task, feedback="Personas are too generic. Add specific demographics and quantified pain points.")
    print(json.dumps(spec2, indent=2))
    print("✓ Revision run completed")


if __name__ == "__main__":
    test_product_agent()
