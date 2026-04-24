import sys
import json
from dotenv import load_dotenv

load_dotenv()

import message_bus
from crew import LaunchMindCrew

BANNER = """
╔══════════════════════════════════════╗
║          LaunchMind                  ║
║  AI Multi-Agent Startup Studio       ║
╚══════════════════════════════════════╝
"""


def main():
    print(BANNER)

    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        idea = input("Enter your startup idea: ").strip()

    if not idea:
        print("No idea provided. Exiting.")
        sys.exit(1)

    crew = LaunchMindCrew()
    result = crew.run(idea)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Tagline  : {result['tagline']}")
    print(f"PR       : {result['pr_url']}")
    print(f"Issue    : {result['issue_url']}")
    print(f"QA       : {result['qa_verdict']}")

    print("\n" + "=" * 60)
    print("FULL MESSAGE LOG")
    print("=" * 60)
    print(json.dumps(message_bus.full_log(), indent=2))


if __name__ == "__main__":
    main()
