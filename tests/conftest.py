"""Use a unique, test-only signing key without weakening production fail-closed behavior."""
import os
import secrets
import pytest


@pytest.fixture(scope="session", autouse=True)
def temporary_audit_key():
    prior = os.environ.get("AUDIT_SECRET_KEY")
    if prior is None:
        os.environ["AUDIT_SECRET_KEY"] = secrets.token_hex(32)
    yield
    if prior is None:
        os.environ.pop("AUDIT_SECRET_KEY", None)
