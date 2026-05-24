from backend.config import SHORT_TERM_MAX_TURNS

_store: dict[str, list] = {}   # session_id -> list of {role, content}

class ShortTermMemory:
    """
    In-memory conversation history per session.
    Keeps last SHORT_TERM_MAX_TURNS turns.
    """
    def add(self, session_id: str, role: str, content: str):
        if session_id not in _store:
            _store[session_id] = []
        _store[session_id].append({"role": role, "content": content})
        # Trim to max turns (each turn = 2 messages)
        max_msgs = SHORT_TERM_MAX_TURNS * 2
        if len(_store[session_id]) > max_msgs:
            _store[session_id] = _store[session_id][-max_msgs:]

    def get(self, session_id: str) -> list:
        return _store.get(session_id, [])

    def clear(self, session_id: str):
        _store.pop(session_id, None)
