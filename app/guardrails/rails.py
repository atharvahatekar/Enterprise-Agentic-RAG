import logfire
import re
from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails

from app.config import settings
from app.guardrails.colang_rules import (
    COLANG_CONTENT,
    JAILBREAK_RESPONSE,
    RAIL_INDICATORS,
    YAML_CONTENT,
)


_rails: LLMRails | None = None

_ROLE_OVERRIDE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE | re.DOTALL)
    for pattern in (
        r"\b(?:ignore|disregard|forget|override|bypass)\b.{0,80}\b(?:instructions?|system(?:\s+prompt)?|rules?|guidelines?|role|persona)\b",
        r"\b(?:act|behave|respond|pretend)\s+as(?:\s+if)?\b",
        r"\b(?:pretend|roleplay)\s+(?:to be|that you are|you are)\b",
        r"\bimpersonate\s+(?:an?\s+)?[a-z]",
        r"\bfrom now on\b.{0,60}\b(?:you are|act as|behave as|respond as)\b",
        r"\b(?:you are|you're)\s+now\s+(?:an?\s+)?[a-z]",
        r"\b(?:become|turn into|transform into)\s+(?:an?\s+)?[a-z]",
        r"\b(?:switch|change)\s+(?:your|the)\s+(?:role|persona|identity)\b",
        r"\bchange\s+(?:yourself\s+)?from\b.{0,60}\bto\b",
        r"\b(?:new|updated|replacement)\s+(?:system\s+)?instructions?\s*(?:are|:)",
        r"\b(?:reveal|show|repeat|print)\b.{0,50}\b(?:system prompt|hidden instructions?)\b",
    )
)


def is_role_override_attempt(message: str) -> bool:
    """Detect explicit attempts to replace or expose the assistant's fixed role."""
    return any(pattern.search(message) for pattern in _ROLE_OVERRIDE_PATTERNS)


def initialize_rails() -> None:
    """
    Build the NeMo LLMRails singleton at app startup.
    Uses llama-3.1-8b-instant for fast intent classification at the gate —
    the heavier llama-3.3-70b-versatile is reserved for the RAG pipeline.
    """
    global _rails

    guard_llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0
    )

    config = RailsConfig.from_content(
        colang_content=COLANG_CONTENT,
        yaml_content=YAML_CONTENT
    )

    _rails = LLMRails(config, llm=guard_llm)
    logfire.info("🛡️ NeMo Guardrails initialised (llama-3.1-8b-instant).")
    
    


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through the NeMo rails gate.

    Returns:
        (True,  rail_response) — a rail fired; return this response immediately,
                                skip the RAG pipeline entirely.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    # Deterministic first line of defence. Semantic intent classification alone
    # can miss novel phrasings such as "change from assistant to a YouTuber".
    if is_role_override_attempt(message):
        logfire.info("🛡️ Deterministic role-override rail fired.")
        return True, JAILBREAK_RESPONSE

    if _rails is None:
        logfire.warning("⚠️ Guardrails not initialised — skipping gate.")
        return False, None

    with logfire.span("🛡️ Guardrails Check"):
        result = _rails.generate(messages=[{"role": "user", "content": message}])

        # NeMo returns {'role': 'assistant', 'content': '...'} — extract text
        content = result.get("content", "") if isinstance(result, dict) else str(result)

        normalized_content = content.casefold()
        fired = any(
            indicator.casefold() in normalized_content
            for indicator in RAIL_INDICATORS
        )

        if fired:
            logfire.info(f"🛡️ Guardrails fired | query='{message[:80]}'")
            return True, content

        logfire.info("✅ Guardrails passed.")
        return False, None
