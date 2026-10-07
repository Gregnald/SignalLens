from app.services.severity_service import rule_based_severity, validate_severity


def test_critical_keywords_detected():
    assert rule_based_severity(["Payment failed and money was deducted from my account"]) == "critical"


def test_high_keywords_detected():
    assert rule_based_severity(["The app crashes every time I open it"]) == "high"


def test_medium_keywords_detected():
    assert rule_based_severity(["The UI is a bit slow and laggy"]) == "medium"


def test_low_default_for_cosmetic_feedback():
    assert rule_based_severity(["I wish the icon was a different color"]) == "low"


def test_validate_severity_upgrades_underrated_llm_output():
    # LLM said "low" but the text clearly describes a critical payment failure
    result = validate_severity("low", ["money deducted but transaction failed"])
    assert result == "critical"


def test_validate_severity_never_downgrades_llm_critical():
    result = validate_severity("critical", ["minor cosmetic issue with the icon"])
    assert result == "critical"


def test_validate_severity_handles_invalid_llm_value():
    result = validate_severity("not-a-real-severity", ["app crashes constantly"])
    assert result == "high"
