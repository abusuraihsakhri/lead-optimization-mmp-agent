"""FastAPI interface for the generic audit workflow."""
import hmac
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")
app = FastAPI(
    title="Lead Optimization MMP Agent — Generic Audit API",
    description="Deterministic generic threshold checks; not structural matched molecular pair analysis.",
    version="3.0.1",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/")
def home():
    page = Path(__file__).resolve().parent.parent / "web" / "index.html"
    if not page.is_file():
        raise HTTPException(status_code=404, detail="Web client unavailable in this installation")
    return FileResponse(page, media_type="text/html")


@app.get("/health")
def health():
    try:
        AuditLogger.verify_integrity()
    except (RuntimeError, ValueError):
        raise HTTPException(status_code=503, detail="AUDIT_SECRET_KEY is not configured")
    return {"status": "HEALTHY", "service": "lead-optimization-mmp-agent", "version": "3.0.1"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "metric_format": "json"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        return supervisor.process_task(payload).to_dict()
    except SecurityException:
        raise HTTPException(status_code=400, detail="Sensitive identifier detected in submitted payload")


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Sensitive identifier detected in query")


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: str = Header(default="")):
    configured = os.environ.get("AUDIT_READ_TOKEN", "")
    if not configured:
        raise HTTPException(status_code=404, detail="Audit log endpoint is disabled")
    if not hmac.compare_digest(x_audit_token, configured):
        raise HTTPException(status_code=403, detail="Access denied")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
