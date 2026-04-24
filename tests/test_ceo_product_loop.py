"""
Tests CEO → Product feedback loop via message bus.
Run: .venv/bin/python -m tests.test_ceo_product_loop
"""
import json
import message_bus
from agents.ceo_agent import CEOAgent

IDEA = (
    "melon — a beautiful open-source voice assistant focused on preserving user privacy. "
    "Cross-platform desktop app (Electron) that downloads local transcription models, "
    "records voice, and converts speech to text for clipboard use."
)


def test_ceo_product_loop():
    message_bus.reset()

    print("\n=== CEO → Product Loop Test ===")
    print(f"Idea: {IDEA[:80]}...")

    ceo = CEOAgent()
    result = ceo.run(IDEA)

    print("\n--- Final Spec ---")
    print(json.dumps(result["spec"], indent=2))

    print("\n--- Review Result ---")
    print(json.dumps(result["review"], indent=2))

    print("\n--- Full Message Log ---")
    for msg in message_bus.full_log():
        print(f"  [{msg['timestamp']}] {msg['from_agent']} → {msg['to_agent']} ({msg['message_type']})")

    # Assertions
    assert result["spec"] is not None, "No spec produced"
    assert "value_proposition" in result["spec"], "Spec missing value_proposition"

    msgs = message_bus.full_log()
    assert any(m["message_type"] == "task" and m["to_agent"] == "product" for m in msgs), \
        "No task sent to product"
    assert any(m["message_type"] == "confirmation" and m["from_agent"] == "product" for m in msgs), \
        "No confirmation from product"

    print("\n✓ All assertions passed")


if __name__ == "__main__":
    test_ceo_product_loop()
