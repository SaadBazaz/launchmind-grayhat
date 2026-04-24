# Module 07 — Main Entrypoint

## Goal

Single command runs the entire pipeline end-to-end. Startup idea comes from CLI arg or interactive prompt — never hardcoded.

## File

`main.py`

## Startup Idea Input

```python
import sys

if len(sys.argv) > 1:
    idea = " ".join(sys.argv[1:])
else:
    idea = input("Enter your startup idea: ").strip()
```

## Execution Order

```
1. Load .env (python-dotenv)
2. Print banner: "LaunchMind starting with idea: {idea}"
3. ceo.run(idea)
   └── internally orchestrates product → engineer → marketing → qa
4. Print full message log (message_bus.full_log())
```

## Terminal Output Requirements (for demo)

Every agent must print to stdout when it:
- Receives a message
- Starts an LLM call
- Completes a platform action (GitHub, Slack, email)
- Sends a message

Format: `[AGENT_NAME] action description`

Example:
```
[CEO] Decomposing idea via LLM...
[CEO] → Sending task to product agent
[PRODUCT] Received task. Generating product spec...
[PRODUCT] → Sending spec to engineer and marketing
[CEO] Reviewing product spec via LLM... verdict=pass
[ENGINEER] Generating landing page HTML...
[ENGINEER] Created GitHub issue: https://github.com/.../issues/1
[ENGINEER] Committed index.html to branch agent-landing-page-a1b2c3d4
[ENGINEER] Opened PR: https://github.com/.../pull/1
[MARKETING] Generating marketing copy...
[MARKETING] Email sent to test@example.com
[MARKETING] Slack message posted to #launches
[QA] Reviewing HTML and copy...
[QA] Posted PR review comments
[QA] Overall verdict: fail
[CEO] QA failed — sending revision request to engineer
[ENGINEER] Revising landing page...
[ENGINEER] Updated PR with revised HTML
[CEO] Posting final summary to Slack
[CEO] Pipeline complete.
```

## Final Output

After pipeline completes, print:
```
=== FULL MESSAGE LOG ===
[JSON of all messages]
=== END ===
```

## Error Handling

- Wrap each agent run in `try/except`. On failure, print `[AGENT_NAME] ERROR: {e}` and continue. Do not crash the entire pipeline on a single agent failure (bonus marks for graceful handling).
