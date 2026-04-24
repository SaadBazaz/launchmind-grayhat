# Module 00 — Project Setup

## Goal

Repo, secrets, and dependencies ready before any agent code is written.

## Steps

1. Confirm repo is public at `github.com/<user>/launchmind-grayhat`.
2. Create `.gitignore` with `.env` listed.
3. Create `.env` with all required keys (already present — do not commit).
4. Create `.env.example` with placeholder values for every key.
5. Create `requirements.txt`.

## Required Environment Variables

```
ANTHROPIC_API_KEY=
GITHUB_TOKEN=
GITHUB_REPO=          # e.g. saadbazaz/launchmind-grayhat
SLACK_BOT_TOKEN=
SLACK_CHANNEL=        # e.g. #launches
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=  # verified sender in SendGrid
EMAIL_TO=             # test inbox to receive cold outreach
```

## `requirements.txt` Contents

```
anthropic
crewai
requests
sendgrid
python-dotenv
```

## Verification Checklist

- [ ] `python -c "import anthropic, crewai, sendgrid"` exits cleanly
- [ ] `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user` returns your username
- [ ] SendGrid test send arrives in `EMAIL_TO` inbox
- [ ] Slack bot test message appears in `SLACK_CHANNEL`
