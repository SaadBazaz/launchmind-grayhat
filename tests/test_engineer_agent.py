"""
Independent test for EngineerAgent.
Run: .venv/bin/python -m tests.test_engineer_agent
"""
import json
import message_bus
from agents.engineer_agent import EngineerAgent

SAMPLE_SPEC = {
    "value_proposition": "Melon lets privacy-conscious users transcribe speech to text locally, with no data leaving their device.",
    "personas": [
        {"name": "Sara", "role": "Journalist", "pain_point": "Transcribing interviews without uploading sensitive audio to cloud services"},
        {"name": "Dev", "role": "Developer", "pain_point": "Needs offline speech-to-text for CLI workflows"},
    ],
    "features": [
        {"name": "Local Transcription", "description": "Downloads and runs Whisper models locally — no cloud.", "priority": 1},
        {"name": "Clipboard Export", "description": "One-click copy of transcribed text to clipboard.", "priority": 2},
        {"name": "Model Selector", "description": "Choose transcription model size vs. speed tradeoff.", "priority": 3},
        {"name": "Recording Controls", "description": "Push-to-talk and toggle recording modes.", "priority": 4},
        {"name": "Cross-Platform", "description": "Works on macOS, Windows, and Linux via Electron.", "priority": 5},
    ],
    "user_stories": [
        {"as_a": "journalist", "i_want": "to record and transcribe interviews offline", "so_that": "sensitive sources are never exposed to cloud providers"},
        {"as_a": "developer", "i_want": "to pipe transcribed text into my CLI tools", "so_that": "I can automate note-taking without leaving the terminal"},
        {"as_a": "student", "i_want": "to transcribe lectures locally", "so_that": "my voice data stays on my own machine"},
    ],
}


def test_engineer_agent():
    message_bus.reset()

    # Simulate message from product agent
    task_msg = {
        "message_id": "test-engineer-001",
        "from_agent": "product",
        "to_agent": "engineer",
        "message_type": "result",
        "payload": {"spec": SAMPLE_SPEC},
        "timestamp": "2026-01-01T00:00:00Z",
        "parent_message_id": None,
    }

    print("\n=== EngineerAgent Test ===")
    agent = EngineerAgent()
    result = agent.run(task_msg)

    print("\n--- Result ---")
    print(json.dumps({k: v for k, v in result.items() if k != "html_preview"}, indent=2))
    print(f"\nHTML preview:\n{result['html_preview'][:200]}...")

    # Assertions
    assert result["pr_url"].startswith("https://github.com/"), f"Bad PR URL: {result['pr_url']}"
    assert result["issue_url"].startswith("https://github.com/"), f"Bad issue URL: {result['issue_url']}"
    assert result["branch"].startswith("agent-landing-page-"), f"Bad branch: {result['branch']}"

    msgs = message_bus.full_log()
    assert any(m["from_agent"] == "engineer" and m["to_agent"] == "ceo" for m in msgs), \
        "Engineer never reported back to CEO"

    print("\n✓ All assertions passed")
    print(f"\nPR:    {result['pr_url']}")
    print(f"Issue: {result['issue_url']}")


if __name__ == "__main__":
    test_engineer_agent()
