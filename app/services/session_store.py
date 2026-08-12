# services/session_store.py
import logging

from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam

type Message = (ChatCompletionSystemMessageParam |
                ChatCompletionUserMessageParam |
                ChatCompletionAssistantMessageParam)

_sessions: dict[str, list[Message]] = dict()

MAX_HISTORY_TURNS = 5
MAX_HISTORY_CHARS = 8000


def get_history(session_id: str) -> list[Message]:
    if not session_id:
        return []
    return _sessions.get(session_id, [])


def append(session_id: str, role: str, content: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    if role == "system":
        _sessions[session_id].append(ChatCompletionSystemMessageParam(role="system", content=content))
    elif role == "user":
        _sessions[session_id].append(ChatCompletionUserMessageParam(role="user", content=content))
    elif role == "assistant":
        _sessions[session_id].append(ChatCompletionAssistantMessageParam(role="assistant", content=content))
    _trim(session_id)


def _trim(session_id: str):
    session = _sessions[session_id]

    while len(session) > MAX_HISTORY_TURNS * 2:
        session = session[2:]

    while sum(len(msg["content"]) for msg in session) > MAX_HISTORY_CHARS:
        session = session[1:]

    _sessions[session_id] = session


def clear(session_id: str):
    if session_id in _sessions:
        _sessions.pop(session_id)
        logging.info(f"Session: {session_id} removed from context")
    else:
        logging.warning(f"Session: {session_id} not present in context")


def get_all_sessions() -> list[str]:
    return [session for session in _sessions]
