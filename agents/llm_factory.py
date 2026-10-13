"""Deterministic mock response adapter. No external model integrations are provided."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Lead Optimization Mmp Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} mock]: No language model was called and no scientific "
            "validation was performed. Received an authorized system query."
        )


class LLMFactory:
    """Construct a supported adapter; do not silently substitute a mock for remote providers."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Lead Optimization Mmp Agent"):
        if str(provider).lower() in {"mock", "deterministic", "test"}:
            return MockLLM(system_name)
        raise NotImplementedError(
            f"Model provider {provider!r} is not implemented. Use 'mock' for deterministic testing."
        )
