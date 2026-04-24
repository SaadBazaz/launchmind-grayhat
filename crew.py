import json
import re
from crewai import Crew, Process
from json_repair import repair_json

import message_bus
from agents.agents import (
    ceo_agent, product_agent, engineer_agent, engineer_agent_json,
    marketing_agent, qa_agent
)
from agents.tasks import (
    make_decompose_task,
    make_product_task,
    make_review_task,
    make_html_task,
    make_pr_meta_task,
    make_marketing_task,
    make_qa_task,
    make_final_summary_task,
)
from agents.github import GitHubClient
from agents.slack import post_launch_message, post_ceo_summary
from agents.email import send_cold_outreach


def _run(agents, tasks) -> str:
    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    ).kickoff().raw


def _parse_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    # Extract first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    # Try clean parse first, then repair
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(repair_json(text))


def _log(from_agent, to_agent, msg_type, payload, parent_id=None):
    return message_bus.send(from_agent, to_agent, msg_type, payload, parent_id)


class LaunchMindCrew:
    def __init__(self):
        self._gh = GitHubClient()

    def run(self, idea: str) -> dict:
        print(f"\n[LAUNCHMIND] Starting pipeline for: {idea}\n")

        # ── Phase 1: CEO decomposes idea ─────────────────────────────────────
        print("[LAUNCHMIND] Phase 1: Decomposing idea...")
        decompose_raw = _run([ceo_agent], [make_decompose_task(idea)])
        tasks_json = _parse_json(decompose_raw)
        product_focus = tasks_json["product_task"]["focus"]
        print(f"[LAUNCHMIND] Tasks generated: {list(tasks_json.keys())}")

        ceo_task_msg = _log("ceo", "product", "task", {
            "idea": idea,
            "focus": product_focus,
            "context": tasks_json["product_task"]["context"],
        })

        # ── Phase 2: Product spec with feedback loop ──────────────────────────
        spec = None
        review = None
        for attempt in range(2):
            print(f"\n[LAUNCHMIND] Phase 2: Product spec (attempt {attempt + 1})...")
            feedback = review.get("feedback") if review else None

            product_raw = _run(
                [product_agent],
                [make_product_task(idea, product_focus, feedback)],
            )
            spec = _parse_json(product_raw)
            spec_str = json.dumps(spec, indent=2)

            # CEO reviews spec
            print("[LAUNCHMIND] CEO reviewing product spec...")
            review_raw = _run([ceo_agent], [make_review_task(spec_str)])
            review = _parse_json(review_raw)
            verdict = review.get("verdict", "pass")
            print(f"[LAUNCHMIND] Review verdict: {verdict} — {review.get('reason', '')[:80]}")

            _log("product", "ceo", "confirmation", {"status": "ready", "spec": spec},
                 ceo_task_msg["message_id"])

            if verdict == "pass":
                break

            if attempt == 0:
                rev_msg = _log("ceo", "product", "revision_request", {
                    "idea": idea, "focus": product_focus,
                    "feedback": review.get("feedback"),
                }, ceo_task_msg["message_id"])
                print(f"[LAUNCHMIND] Revision requested: {review.get('feedback', '')[:80]}")
            else:
                print("[LAUNCHMIND] Accepting spec after 2 attempts.")

        spec_str = json.dumps(spec, indent=2)
        _log("product", "engineer", "result", {"spec": spec})
        _log("product", "marketing", "result", {"spec": spec})

        # ── Phase 3: Engineer — HTML + GitHub ────────────────────────────────
        print("\n[LAUNCHMIND] Phase 3: Engineer building landing page...")
        html_raw = _run([engineer_agent], [make_html_task(spec_str)])
        # Strip code fences if model returned them
        html = html_raw.strip()
        if html.startswith("```"):
            html = re.sub(r"^```[a-z]*\n?", "", html)
            html = re.sub(r"\n?```$", "", html).strip()

        pr_meta_raw = _run([engineer_agent], [make_pr_meta_task(spec_str)])
        pr_meta = _parse_json(pr_meta_raw)

        issue_desc_task_desc = spec.get("value_proposition", "Initial landing page")
        issue_url = self._gh.create_issue("Initial landing page", issue_desc_task_desc)

        branch = self._gh.new_branch_name()
        base_sha = self._gh.get_main_sha()
        self._gh.create_branch(branch, base_sha)
        self._gh.commit_file(branch, "index.html", html, "Add landing page [EngineerAgent]")
        pr_url = self._gh.create_pr(branch, pr_meta["title"], pr_meta["body"])
        pull_number = int(pr_url.rstrip("/").split("/")[-1])

        print(f"[LAUNCHMIND] PR opened: {pr_url}")
        _log("engineer", "ceo", "result", {
            "pr_url": pr_url, "issue_url": issue_url, "branch": branch,
        })

        # ── Phase 4: Marketing — copy + email + Slack ─────────────────────────
        print("\n[LAUNCHMIND] Phase 4: Marketing generating copy...")
        marketing_raw = _run([marketing_agent], [make_marketing_task(spec_str)])
        copy = _parse_json(marketing_raw)

        tagline = copy.get("tagline", "Launch with AI")
        description = copy.get("landing_description", "")
        cold_email = copy.get("cold_email", {})

        print("[LAUNCHMIND] Sending cold outreach email...")
        send_cold_outreach(cold_email.get("subject", "Check this out"), cold_email.get("body", ""))
        print(f"[LAUNCHMIND] Email sent to {__import__('os').environ['EMAIL_TO']}")

        print("[LAUNCHMIND] Posting launch message to Slack...")
        post_launch_message(tagline, description, pr_url)
        print("[LAUNCHMIND] Slack message posted.")

        _log("marketing", "ceo", "result", {
            "tagline": tagline,
            "email_sent": True,
            "slack_posted": True,
            "copy": copy,
        })

        # ── Phase 5: QA review ───────────────────────────────────────────────
        print("\n[LAUNCHMIND] Phase 5: QA reviewing outputs...")
        qa_raw = _run(
            [qa_agent],
            [make_qa_task(spec_str, html, json.dumps(copy))],
        )
        qa = _parse_json(qa_raw)
        qa_verdict = qa.get("overall_verdict", "pass")
        print(f"[LAUNCHMIND] QA verdict: {qa_verdict}")

        # Post PR review comments
        pr_comments = qa.get("pr_comments", ["Automated QA review complete."])
        try:
            self._gh.add_pr_review(pull_number, pr_comments)
            print("[LAUNCHMIND] PR review comments posted.")
        except Exception as e:
            print(f"[LAUNCHMIND] PR review warning: {e}")

        _log("qa", "ceo", "result", {"overall_verdict": qa_verdict, "review": qa})

        # If QA fails, engineer revises
        if qa_verdict == "fail":
            print("\n[LAUNCHMIND] QA failed — requesting engineer revision...")
            issues = (
                qa.get("html_review", {}).get("issues", []) +
                qa.get("copy_review", {}).get("issues", [])
            )
            rev_msg = _log("ceo", "engineer", "revision_request", {
                "pr_url": pr_url, "branch": branch, "issues": issues,
            })

            revised_html_raw = _run(
                [engineer_agent],
                [make_html_task(spec_str + f"\n\nRevise to fix these issues: {issues}")],
            )
            revised_html = revised_html_raw.strip()
            if revised_html.startswith("```"):
                revised_html = re.sub(r"^```[a-z]*\n?", "", revised_html)
                revised_html = re.sub(r"\n?```$", "", revised_html).strip()

            self._gh.commit_file(
                branch, "index.html", revised_html,
                "Revise landing page per QA feedback [EngineerAgent]",
            )
            _log("engineer", "ceo", "result", {
                "pr_url": pr_url, "branch": branch, "revised": True,
            })
            print(f"[LAUNCHMIND] Revised HTML committed to {branch}.")

        # ── Phase 6: CEO final Slack summary ─────────────────────────────────
        print("\n[LAUNCHMIND] Phase 6: CEO posting final summary...")
        summary_raw = _run(
            [ceo_agent],
            [make_final_summary_task(spec_str, pr_url, qa_verdict)],
        )
        post_ceo_summary(summary_raw.strip(), pr_url)
        print("[LAUNCHMIND] Final summary posted to Slack.")

        print("\n[LAUNCHMIND] Pipeline complete.")
        return {
            "spec": spec,
            "pr_url": pr_url,
            "issue_url": issue_url,
            "qa_verdict": qa_verdict,
            "tagline": tagline,
        }
