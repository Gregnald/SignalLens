from app.models.dataset import Dataset
from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.theme import Theme
from app.services import evidence_service, impact_service
from tests.conftest import requires_db


@requires_db
def test_collect_evidence_creates_representative_and_temporal_items(db_session):
    dataset = Dataset(name="evidence-test")
    db_session.add(dataset)
    db_session.flush()

    theme = Theme(
        dataset_id=dataset.id,
        name="Payment Failure",
        severity="critical",
        volume=10,
        growth_percent=327.0,
        impact_score=94.0,
    )
    db_session.add(theme)
    db_session.flush()

    incident = Incident(
        dataset_id=dataset.id,
        theme_id=theme.id,
        title="Payment Failure",
        severity="critical",
        impact_score=94.0,
        growth_percent=327.0,
        likely_driver="Android v4.8.1",
        root_cause_confidence=88.0,
    )
    db_session.add(incident)
    db_session.commit()

    created = evidence_service.collect_evidence(db_session, dataset.id)

    assert created >= 2  # at least the temporal + driver evidence items
    evidence_rows = db_session.query(Evidence).filter(Evidence.incident_id == incident.id).all()
    types = {e.evidence_type for e in evidence_rows}
    assert "temporal_statistic" in types
    assert "segment_concentration" in types


@requires_db
def test_calculate_impact_scores_ranks_higher_severity_theme_higher(db_session):
    dataset = Dataset(name="impact-test")
    db_session.add(dataset)
    db_session.flush()

    critical_theme = Theme(
        dataset_id=dataset.id,
        name="Critical Issue",
        severity="critical",
        volume=100,
        growth_percent=200.0,
        negative_percent=90.0,
        confidence=0.9,
    )
    low_theme = Theme(
        dataset_id=dataset.id,
        name="Low Issue",
        severity="low",
        volume=5,
        growth_percent=0.0,
        negative_percent=10.0,
        confidence=0.5,
    )
    db_session.add_all([critical_theme, low_theme])
    db_session.commit()

    impact_service.calculate_impact_scores(db_session, dataset.id)

    db_session.refresh(critical_theme)
    db_session.refresh(low_theme)
    assert critical_theme.impact_score > low_theme.impact_score
