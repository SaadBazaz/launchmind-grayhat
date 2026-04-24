# Module 04 — Engineer Agent

## Goal

Read product spec, generate HTML landing page via LLM, create GitHub issue, commit HTML to new branch, open pull request. Return PR URL and issue URL to CEO.

## File

`agents/engineer_agent.py`

## Inputs

- Product spec JSON (from message bus, sent by Product agent)
- Task context from CEO message (via message bus)

## LLM Calls

### Call 1 — Landing Page HTML

**System prompt:** You are a frontend engineer. Generate a complete, self-contained HTML landing page for a startup. Include: headline, subheadline, features section (list each feature by name), a call-to-action button, and inline CSS. Return only the raw HTML — no markdown, no explanation.

**User prompt:** Serialised product spec (value_proposition, features list).

**Output:** Raw HTML string.

### Call 2 — PR Title and Body

**System prompt:** You are a software engineer writing a GitHub pull request description. Given a product spec, write a short PR title (under 72 chars) and a markdown body describing what was built and why. Return JSON: `{ "title": "...", "body": "..." }`.

**User prompt:** Serialised product spec.

### Call 3 — GitHub Issue Description

**System prompt:** You are a software engineer creating a GitHub issue. Write a concise issue description (2–3 sentences) for an initial landing page implementation task. Return only the description text.

**User prompt:** `value_proposition` from product spec.

## GitHub API Flow

All calls use `requests` + `GITHUB_TOKEN` env var. `GITHUB_REPO` = `owner/repo`.

```
1. GET /repos/{GITHUB_REPO}/git/ref/heads/main → get base SHA
2. POST /repos/{GITHUB_REPO}/issues → create issue, save issue_url
3. POST /repos/{GITHUB_REPO}/git/refs → create branch "agent-landing-page-{uuid[:8]}"
4. PUT  /repos/{GITHUB_REPO}/contents/index.html → commit HTML (base64 encoded)
     author: { "name": "EngineerAgent", "email": "agent@launchmind.ai" }
5. POST /repos/{GITHUB_REPO}/pulls → open PR (head=branch, base=main)
     title and body from LLM Call 2
6. Return pr_url, issue_url
```

## Outputs (via message bus)

```
send(engineer → ceo, result, payload={
  "pr_url": "https://github.com/...",
  "issue_url": "https://github.com/...",
  "branch": "agent-landing-page-xxxx",
  "html_preview": "<first 200 chars of HTML>"
})
```

## Revision Handling

If `revision_request` from CEO (triggered by QA fail):
- Extract issues from payload
- Re-run LLM Call 1 with appended instruction: "Revise the landing page to fix these issues: {issues}"
- Commit revised HTML to same branch (the PUT endpoint updates the file when `sha` of existing blob is provided)
- Re-send result to CEO

## Constraints

- `GITHUB_TOKEN` loaded from env — never hardcoded.
- Branch name must be unique per run (use UUID suffix) to avoid conflicts on re-runs.
- Commit author must be `EngineerAgent <agent@launchmind.ai>`.
