from pydantic import BaseModel


class ChatRequest(BaseModel):
    dataset_id: int
    question: str


class ChatMetric(BaseModel):
    label: str
    value: str


class ChatAnswer(BaseModel):
    """Structured output schema the LLM must fill for an investigator answer."""

    answer: str
    cited_incident_ids: list[int] = []
    cited_evidence_ids: list[int] = []


class ChatResponse(BaseModel):
    answer: str
    evidence_ids: list[int] = []
    metrics: list[ChatMetric] = []
    incident_ids: list[int] = []
    generated_by: str
