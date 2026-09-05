"""
Automated Pytest Test Suite for Lead Optimization Mmp Agent.
Domain: AI Drug Discovery, Structural Biology & Wet-Lab Robotics
Standard: wwPDB / IUPAC / OpenSMILES / ISAC Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567 or MRN-12345")
    assert "[REDACTED_IDENTIFIER]" in redacted
    assert "555-123-4567" not in redacted
    assert "MRN-12345" not in redacted


def test_phi_guard_email_blocked():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Send results to patient@hospital.org")


def test_phi_guard_ssn_blocked():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient SSN: 123-45-6789")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_model_validation_rejects_nan():
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=float("nan"))


def test_model_validation_rejects_inf():
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=float("inf"))


def test_model_validation_rejects_empty_task_id():
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="", target_identifier="KEY-01", primary_metric=10.0)


def test_audit_trail_requires_secret_key(monkeypatch):
    monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
    from agents.base import _GLOBAL_AUDIT
    import agents.base as base_mod
    # Reset global to force re-initialization
    base_mod._GLOBAL_AUDIT = None
    with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
        AuditTrail()


def test_audit_trail_rejects_short_key():
    with pytest.raises(ValueError, match="at least 16 characters"):
        AuditTrail(secret_key="short")


def test_audit_trail_integrity_tampering():
    trail = AuditTrail(secret_key="test-integration-key-2026")
    trail.log("test", "tier", "EVENT", {"data": "value1"})
    trail.log("test", "tier", "EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True
    # Tamper with a log entry
    trail.logs[0]["payload_hash"] = "tampered_hash_value"
    assert trail.verify_integrity() is False


def test_batch_cli_missing_file():
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1
