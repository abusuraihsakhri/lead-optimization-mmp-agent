"""Optional FastAPI server for the legacy deterministic threshold evaluator."""
from typing import Dict, Any

from .models import FrontierPayload
from .agents import MMPOptimizerCoordinator

coordinator = MMPOptimizerCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
    except ImportError:
        return None

    app = FastAPI(
        title="MMP Optimizer — Generic Threshold Evaluator",
        description=(
            "Deterministic numeric threshold and descriptor screening. "
            "Does not identify molecular transformations or predict potency or patentability."
        ),
        version="2.0.1",
    )

    class TaskRequest(BaseModel):
        task_id: str = "TASK-2026-001"
        target_identifier: str = "TARGET-BIO-KEY"
        primary_metric: float = 28.5
        secondary_metric: float = 14.2
        status_descriptor: str = "DISCORDANT_ANOMALY"
        is_critical_flag: bool = True
        attributes: Dict[str, Any] = Field(default_factory=dict)

    class ChatRequest(BaseModel):
        query: str

    @app.get("/health")
    def health():
        return {"status": "HEALTHY", "system": "lead-optimization-mmp-agent", "version": "2.0.1"}

    @app.post("/api/audit")
    def api_audit(req: TaskRequest):
        return coordinator.process(FrontierPayload(
            task_id=req.task_id,
            target_identifier=req.target_identifier,
            primary_metric=req.primary_metric,
            secondary_metric=req.secondary_metric,
            status_descriptor=req.status_descriptor,
            is_critical_flag=req.is_critical_flag,
            attributes=req.attributes,
        ))

    @app.post("/api/chat")
    def api_chat(req: ChatRequest):
        return {"response": coordinator.query_supervisory_chat(req.query)}

    return app
