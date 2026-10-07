"""Rule-based severity taxonomy — ARCHITECTURE.md §11 / §21.
The LLM may propose a severity, but it is validated/overridden by these rules;
rules never downgrade an LLM-flagged critical issue, only upgrade under strong signal.
"""

_CRITICAL_KEYWORDS = {
    "charged twice",
    "duplicate charge",
    "money deducted",
    "money was deducted",
    "lost my money",
    "stolen",
    "fraud",
    "security",
    "privacy",
    "data loss",
    "lost my data",
    "can't access my account",
    "account locked",
    "account inaccessible",
    "payment failed",
    "payment failure",
    "transaction failed",
    "outage",
    "down for everyone",
}

_HIGH_KEYWORDS = {
    "crash",
    "crashes",
    "freezes",
    "freeze",
    "won't open",
    "doesn't open",
    "login failed",
    "can't log in",
    "cannot log in",
    "otp",
    "unusable",
    "stopped working",
}

_MEDIUM_KEYWORDS = {
    "slow",
    "lag",
    "laggy",
    "bug",
    "glitch",
    "incorrect",
    "wrong result",
    "confusing",
    "ui",
    "ux",
}

_SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def rule_based_severity(sample_texts: list[str]) -> str:
    joined = " ".join(sample_texts).lower()
    if any(k in joined for k in _CRITICAL_KEYWORDS):
        return "critical"
    if any(k in joined for k in _HIGH_KEYWORDS):
        return "high"
    if any(k in joined for k in _MEDIUM_KEYWORDS):
        return "medium"
    return "low"


def validate_severity(llm_severity: str, sample_texts: list[str]) -> str:
    llm_severity = llm_severity.lower() if llm_severity else "low"
    if llm_severity not in _SEVERITY_RANK:
        llm_severity = "low"
    rule_severity = rule_based_severity(sample_texts)

    if _SEVERITY_RANK[rule_severity] > _SEVERITY_RANK[llm_severity]:
        return rule_severity
    return llm_severity
