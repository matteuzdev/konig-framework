"""Fail-closed evidence contracts for live agent execution.

This module is additive and does not alter existing engineering workflows.
"""
from dataclasses import dataclass
from enum import Enum


class OutputOrigin(str, Enum):
    PROVIDER = "provider"
    TEMPLATE = "template"
    SIMULATED = "simulated"


class UnverifiedExecutionError(RuntimeError):
    """Raised when a synthetic result is submitted as verified execution."""


@dataclass(frozen=True)
class ExecutionEvidence:
    origin: OutputOrigin
    content: str
    provider_request_id: str | None = None
    test_exit_code: int | None = None
    artifact_reference: str | None = None

    def require_real_generation(self) -> None:
        if self.origin is not OutputOrigin.PROVIDER or not self.provider_request_id:
            raise UnverifiedExecutionError(
                "Live generation requires provider origin and a request ID"
            )

    def require_verified_test(self) -> None:
        if self.origin is not OutputOrigin.PROVIDER or self.test_exit_code != 0:
            raise UnverifiedExecutionError(
                "Verified QA requires an actual successful test execution"
            )

    def require_artifact(self) -> None:
        if not self.artifact_reference:
            raise UnverifiedExecutionError("A concrete artifact reference is required")
