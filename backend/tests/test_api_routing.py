"""Regression tests for route-registration-order bugs — FastAPI/Starlette matches
routes in registration order and does not backtrack past a syntactic match, so two
routers mounted at the same prefix with same-segment-count patterns can silently
shadow each other (see app/main.py for the real incident this caught).
"""

from fastapi.testclient import TestClient

from app.main import app
from app.models.dataset import Dataset
from app.models.incident import Incident
from app.models.theme import Theme
from tests.conftest import requires_db


@requires_db
def test_incident_evidence_route_is_not_shadowed_by_dataset_incident_route(db_session):
    """GET /api/incidents/{incident_id}/evidence must resolve to the evidence handler,
    not to GET /api/incidents/{dataset_id}/{incident_id} (which would try to parse the
    literal "evidence" segment as an incident_id and 422).
    """
    dataset = Dataset(name="routing-test")
    db_session.add(dataset)
    db_session.flush()

    theme = Theme(dataset_id=dataset.id, name="Routing Theme")
    db_session.add(theme)
    db_session.flush()

    incident = Incident(dataset_id=dataset.id, theme_id=theme.id, title="Routing Incident")
    db_session.add(incident)
    db_session.commit()

    def override_get_db():
        yield db_session

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/incidents/{incident.id}/evidence")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200, response.json()
    assert response.json() == []
