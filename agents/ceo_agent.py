import json
import message_bus
from agents.base_agent import BaseAgent
from agents.product_agent import ProductAgent

DECOMPOSE_SYSTEM = """You are the CEO of an AI startup studio.
Given a startup idea, produce a JSON task list for your team.
Return ONLY this JSON structure:
{
  "product_task": {"focus": "string", "context": "string"},
  "engineer_task": {"focus": "string", "context": "string"},
  "marketing_task": {"focus": "string", "context": "string"}
}
Each focus is a one-sentence directive. Context adds any relevant detail."""

REVIEW_SYSTEM = """You are a critical startup CEO reviewing a product specification.
Evaluate whether it is specific, realistic, and complete.
Return ONLY this JSON:
{
  "verdict": "pass" or "fail",
  "reason": "one sentence",
  "feedback": "specific revision instructions if fail, else null"
}
Be strict — vague personas or generic features should fail."""

SLACK_SUMMARY_SYSTEM = """You are writing a concise Slack update as a startup CEO.
Given a product spec and PR URL, write a one-paragraph launch summary (3-4 sentences).
Return plain text only — no markdown, no headers."""


class CEOAgent(BaseAgent):
    def __init__(self):
        super().__init__("ceo")
        self._product_agent = ProductAgent()

    def run(self, idea: str) -> dict:
        self.log(f"Starting pipeline for idea: {idea}")

        # Step 1: decompose idea into tasks
        self.log("Decomposing idea into tasks...")
        tasks = self.call_llm_json(DECOMPOSE_SYSTEM, f"Startup idea: {idea}")
        self.log(f"Tasks generated: {list(tasks.keys())}")

        # Step 2: send task to product agent
        product_task_msg = message_bus.send(
            "ceo", "product", "task",
            {
                "idea": idea,
                "focus": tasks["product_task"]["focus"],
                "context": tasks["product_task"]["context"],
            },
        )

        # Step 3: run product agent (up to 2 attempts)
        spec = None
        for attempt in range(2):
            latest = message_bus.receive_latest("product")
            spec = self._product_agent.run(latest)

            # Step 4: review product spec
            self.log(f"Reviewing product spec (attempt {attempt + 1})...")
            review = self.call_llm_json(
                REVIEW_SYSTEM,
                f"Product spec:\n{json.dumps(spec, indent=2)}",
            )
            self.log(f"Review verdict: {review.get('verdict')} — {review.get('reason', '')[:80]}")

            if review["verdict"] == "pass":
                break

            if attempt == 0:
                # Send revision request
                message_bus.send(
                    "ceo", "product", "revision_request",
                    {
                        "idea": idea,
                        "focus": tasks["product_task"]["focus"],
                        "context": tasks["product_task"]["context"],
                        "feedback": review["feedback"],
                    },
                    parent_message_id=product_task_msg["message_id"],
                )
            else:
                self.log("Second attempt complete — accepting spec as-is.")

        return {
            "spec": spec,
            "tasks": tasks,
            "review": review,
        }
