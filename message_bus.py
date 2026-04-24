import uuid
from datetime import datetime, timezone

# Keyed by recipient agent name. Each value is a list of message dicts.
_bus: dict[str, list[dict]] = {}


def send(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: dict,
    parent_message_id: str = None,
) -> dict:
    msg = {
        "message_id": str(uuid.uuid4()),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "message_type": message_type,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_message_id": parent_message_id,
    }
    _bus.setdefault(to_agent, []).append(msg)
    print(f"[BUS] {from_agent} → {to_agent} ({message_type})")
    return msg


def receive(agent_name: str) -> list[dict]:
    return list(_bus.get(agent_name, []))


def receive_latest(agent_name: str) -> dict | None:
    msgs = _bus.get(agent_name, [])
    return msgs[-1] if msgs else None


def receive_by_type(agent_name: str, message_type: str) -> list[dict]:
    return [m for m in _bus.get(agent_name, []) if m["message_type"] == message_type]


def full_log() -> list[dict]:
    all_msgs = []
    for msgs in _bus.values():
        all_msgs.extend(msgs)
    return sorted(all_msgs, key=lambda m: m["timestamp"])


def reset() -> None:
    """Clear all messages. Used between test runs."""
    _bus.clear()
