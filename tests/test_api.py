"""API, privacy-boundary, and runtime validation checks."""
import math
import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.llm_factory import LLMFactory
from mmp_optimizer.models import FrontierPayload

client = TestClient(app)


def test_home_renders_real_ui():
    res = client.get("/")
    assert res.status_code == 200
    assert "Paired Potency Explorer" in res.text


def test_health_with_test_secret():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"


def test_nominal_audit_and_metrics():
    payload = {
        "task_id": "TEST-API", "target_identifier": "TARGET-API",
        "primary_metric": 10.0, "secondary_metric": 3.0,
        "status_descriptor": "NOMINAL", "is_critical_flag": False
    }
    response = client.post("/api/audit", json=payload)
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    assert client.get("/metrics").json()["dossiers_processed_total"] >= 1


def test_reject_phi_in_nested_attributes():
    payload = {
        "task_id": "TEST-PHI", "target_identifier": "TARGET-API",
        "primary_metric": 10.0,
        "attributes": {"contact": "patient@hospital.org"}
    }
    response = client.post("/api/audit", json=payload)
    assert response.status_code == 400
    assert "Sensitive identifier" in response.json()["detail"]


def test_audit_logs_are_private_by_default(monkeypatch):
    monkeypatch.delenv("AUDIT_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 404
    monkeypatch.setenv("AUDIT_READ_TOKEN", "example-test-read-only-token")
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "example-test-read-only-token"}).status_code == 200


def test_legacy_payload_rejects_nonfinite():
    with pytest.raises(ValueError):
        FrontierPayload("T1", "K1", float("nan"), 1, "NOMINAL")
    with pytest.raises(ValueError):
        FrontierPayload("T1", "K1", 1, float("inf"), "NOMINAL")


def test_no_silent_external_llm_fallback():
    with pytest.raises(NotImplementedError):
        LLMFactory.create("openai")
