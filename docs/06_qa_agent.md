# Module 06 — QA / Reviewer Agent

## Goal

Review Engineer HTML and Marketing copy against product spec via LLM, post inline PR review comments on GitHub, return structured pass/fail report to CEO.

## File

`agents/qa_agent.py`

## Inputs (from message bus, forwarded by CEO)

- Engineer output: `{ pr_url, html_content, branch }`
- Marketing output: full copy JSON
- Product spec JSON (for comparison)
- `pull_number`: integer extracted from `pr_url`

## LLM Calls

### Call 1 — HTML Review

**System prompt:** You are a QA engineer reviewing an HTML landing page against a product specification. Check: (1) does the headline match the value proposition? (2) are all 5 features mentioned? (3) is there a call-to-action? Return JSON: `{ "verdict": "pass"|"fail", "issues": ["issue1", ...] }`. Issues list empty if pass.

**User prompt:** `{ "spec": product_spec, "html": html_content }`

### Call 2 — Marketing Copy Review

**System prompt:** You are a marketing QA reviewer. Check the copy against the product spec: (1) is the tagline under 10 words and compelling? (2) does the cold email have a clear CTA? (3) is the tone appropriate? Return JSON: `{ "verdict": "pass"|"fail", "issues": ["issue1", ...] }`.

**User prompt:** `{ "spec": product_spec, "copy": marketing_copy }`

## GitHub PR Review Comments

Post at least 2 inline comments on `index.html` using the GitHub Pulls Review API:

```
POST /repos/{GITHUB_REPO}/pulls/{pull_number}/reviews
{
  "body": "QA automated review",
  "event": "COMMENT",
  "comments": [
    { "path": "index.html", "position": 1, "body": "<issue from LLM>" },
    { "path": "index.html", "position": 2, "body": "<second issue or general note>" }
  ]
}
```

- If HTML review passes, post 2 approval comments instead of issue comments.
- `position` refers to line position in the diff — use 1 and 2 for simplicity.

## Overall Verdict

- Overall = "fail" if either HTML or copy verdict is "fail", else "pass".

## Outputs (via message bus)

```
send(qa → ceo, result, payload={
  "overall_verdict": "pass"|"fail",
  "html_review": { "verdict": "...", "issues": [...] },
  "copy_review": { "verdict": "...", "issues": [...] },
  "pr_review_url": "https://github.com/.../pull/N#pullrequestreview-..."
})
```

## Constraints

- If verdict is "fail", CEO must send `revision_request` to Engineer — this is the graded feedback loop.
- `GITHUB_TOKEN` from env for all API calls.
