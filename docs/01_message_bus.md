# Module 01 — Message Bus

## Goal

Single shared Python dict that all agents use to send and receive structured messages. Full message history readable at any point.

## File

`message_bus.py`

## Design

```python
import uuid
from datetime import datetime, timezone

# Keyed by recipient agent name. Each value is a list of message dicts.
_bus: dict[str, list[dict]] = {}

def send(from_agent: str, to_agent: str, message_type: str, payload: dict, parent_message_id: str = None) -> dict:
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
    return msg

def receive(agent_name: str) -> list[dict]:
    return _bus.get(agent_name, [])

def receive_latest(agent_name: str) -> dict | None:
    msgs = _bus.get(agent_name, [])
    return msgs[-1] if msgs else None

def full_log() -> list[dict]:
    all_msgs = []
    for msgs in _bus.values():
        all_msgs.extend(msgs)
    return sorted(all_msgs, key=lambda m: m["timestamp"])
```

## Rules

- Every agent imports `message_bus` and calls only `send` / `receive` / `receive_latest`.
- No agent reads from another agent's queue directly.
- `full_log()` is printed at the end of `main.py` for demo visibility.

## Demo Output

`main.py` must print the full message log at the end, formatted as JSON, so the evaluator can verify every inter-agent message.
