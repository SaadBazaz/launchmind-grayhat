import message_bus
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are an experienced product manager at a startup studio.
Given a startup idea and focus areas, produce a detailed product specification as valid JSON.
Be specific — generic outputs will be rejected and sent back for revision.

Return ONLY this JSON structure, no markdown, no explanation:
{
  "value_proposition": "one sentence describing what the product does and for whom",
  "personas": [
    {"name": "string", "role": "string", "pain_point": "string"}
  ],
  "features": [
    {"name": "string", "description": "string", "priority": 1}
  ],
  "user_stories": [
    {"as_a": "string", "i_want": "string", "so_that": "string"}
  ]
}

Requirements:
- 2–3 personas with distinct, specific pain points
- Exactly 5 features ranked 1 (highest) to 5 (lowest)
- Exactly 3 user stories in standard format
"""


class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__("product")

    def run(self, task_msg: dict) -> dict:
        """Process task message from CEO. Handles initial run and revision requests."""
        payload = task_msg["payload"]
        feedback = payload.get("feedback")
        parent_id = task_msg["message_id"]

        idea = payload.get("idea", "")
        focus = payload.get("focus", "Define core personas and top 5 features")

        user_prompt = f"Startup idea: {idea}\nFocus: {focus}"
        if feedback:
            self.log(f"Revision requested — feedback: {feedback[:80]}")
            user_prompt += f"\n\nYour previous output was rejected. Feedback: {feedback}\nRevise accordingly."

        self.log("Generating product spec...")
        spec = self.call_llm_json(SYSTEM_PROMPT, user_prompt, max_tokens=2000)
        self.log(f"Spec ready — value_prop: {spec.get('value_proposition', '')[:80]}")

        # Broadcast spec to engineer and marketing
        message_bus.send("product", "engineer", "result", {"spec": spec}, parent_id)
        message_bus.send("product", "marketing", "result", {"spec": spec}, parent_id)

        # Confirm to CEO
        confirm = message_bus.send(
            "product", "ceo", "confirmation",
            {"status": "ready", "spec": spec},
            parent_id,
        )
        return spec
