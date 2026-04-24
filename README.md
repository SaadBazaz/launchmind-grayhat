# LaunchMind

> This project was built as a group assignment for the *Agentic AI / Multi-Agent Systems* course at **FAST National University of Computer & Emerging Sciences, Islamabad**, under **Dr. Usama Imtiaz**. It is submitted in partial fulfilment of coursework requirements.

LaunchMind is a Multi-Agent System (MAS) that autonomously runs a micro-startup — from a raw idea all the way to a GitHub pull request, a Slack launch announcement, and a cold outreach email — without any human doing it manually.

You give it one sentence. Five AI agents do the rest.

---

## What It Does

| Agent | Role | Output |
|---|---|---|
| **CEO** | Orchestrates the team, decomposes the idea, reviews outputs, drives revision | Task messages, Slack summary |
| **Product Manager** | Generates product spec — personas, features, user stories | Structured JSON spec |
| **Engineer** | Builds HTML landing page, opens GitHub issue + PR | Live GitHub PR |
| **Marketing** | Writes tagline, cold email, social posts, posts to Slack | Email + Slack message |
| **QA Reviewer** | Reviews HTML and copy against spec, posts PR comments | Pass/fail report + GitHub review |

The CEO agent performs LLM-based review of the Product agent's output and issues a revision request if the spec is too vague — this is the core feedback loop that makes it a real MAS and not just a pipeline.

---

## Architecture

```
main.py
  └── LaunchMindCrew (crew.py)
        ├── Phase 1: CEO decomposes idea → task messages
        ├── Phase 2: Product Agent generates spec
        │     └── CEO reviews → revision_request if fail → Product retries
        ├── Phase 3: Engineer Agent → HTML + GitHub issue + PR
        ├── Phase 4: Marketing Agent → copy + SendGrid email + Slack post
        ├── Phase 5: QA Agent → reviews HTML & copy → GitHub PR comments
        │     └── CEO sends revision_request to Engineer if QA fails
        └── Phase 6: CEO posts final Slack summary
```

All inter-agent communication is logged to a shared message bus (`message_bus.py`) using a structured JSON schema with `message_id`, `from_agent`, `to_agent`, `message_type`, `payload`, `timestamp`, and `parent_message_id`. The full log is printed at the end of every run.

**Tech stack:**
- Agents: [CrewAI](https://docs.crewai.com)
- LLM: Ollama (`qwen2.5:1.5b`) locally — swap via `LLM_PROVIDER` env var
- GitHub: direct `requests` calls to `api.github.com`
- Slack: `chat.postMessage` with Block Kit
- Email: SendGrid Python SDK

---

## Planning & Strategy

All module-level plans live in the [`docs/`](./docs) folder:

| Doc | Contents |
|---|---|
| [GENERAL_APPROACH.md](./docs/GENERAL_APPROACH.md) | Non-compromisables, stack decisions, startup idea |
| [00_project_setup.md](./docs/00_project_setup.md) | Env vars, dependencies, verification |
| [01_message_bus.md](./docs/01_message_bus.md) | Message bus design |
| [02_ceo_agent.md](./docs/02_ceo_agent.md) | CEO orchestration & feedback loop |
| [03_product_agent.md](./docs/03_product_agent.md) | Product spec generation |
| [04_engineer_agent.md](./docs/04_engineer_agent.md) | GitHub API flow |
| [05_marketing_agent.md](./docs/05_marketing_agent.md) | Copy, email, Slack |
| [06_qa_agent.md](./docs/06_qa_agent.md) | QA review & PR comments |
| [07_main_entrypoint.md](./docs/07_main_entrypoint.md) | Entry point & terminal output |

---

## Setup

### 1. Clone & create virtual environment

```bash
git clone https://github.com/SaadBazaz/launchmind-grayhat.git
cd launchmind-grayhat
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. (optional) Run LLM locally

I used Ollama with Qwen2.5:1.5b for local testing:

```bash
# Install from https://ollama.com
ollama pull qwen2.5:1.5b
ollama serve
```

However, you're free to configure another LLM (see the [.env.example](./.env.example)) for more LLM options.

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `OLLAMA_MODEL` | Ollama model name (default: `qwen2.5:1.5b`) |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434`) |
| `GITHUB_TOKEN` | GitHub Personal Access Token with `repo` scope |
| `GITHUB_REPO` | Target repo in `owner/repo` format |
| `SLACK_BOT_TOKEN` | Slack Bot Token (`xoxb-...`) |
| `SLACK_CHANNEL` | Slack channel to post to (e.g. `#launches`) |
| `SENDGRID_API_KEY` | SendGrid API key |
| `SENDGRID_VERIFIED_SENDER_IDENTITY` | Verified sender email in SendGrid |
| `EMAIL_TO` | Recipient address for cold outreach email |

### 4. Run

```bash
# Pass idea as argument
python main.py "melon — open-source privacy-first voice-to-text desktop app"

# Or run interactively
python main.py
```

The full message log is printed at the end of every run.

---

## Repository Structure

```
launchmind-grayhat/
├── agents/
│   ├── agents.py        # CrewAI Agent definitions
│   ├── tasks.py         # CrewAI Task factories
│   ├── github.py        # GitHub API client
│   ├── slack.py         # Slack client
│   └── email.py         # SendGrid client
├── docs/                # Planning documents
├── tests/               # Independent agent tests
├── crew.py              # LaunchMindCrew orchestrator
├── message_bus.py       # Shared inter-agent message log
├── main.py              # Entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Running Tests

```bash
# Test CrewAI agent reasoning (no platform API calls)
python -m tests.test_crew_agents

# Test Engineer agent (creates real GitHub PR)
python -m tests.test_engineer_agent
```
