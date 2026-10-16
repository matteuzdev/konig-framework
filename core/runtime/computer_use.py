"""Opt-in Computer Use contracts for König Assistant.

A provider adapter must implement the protocol. This module intentionally
does not control a machine until an authorized adapter is installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ComputerAction(str, Enum):
    OPEN_URL = "open_url"
    CLICK = "click"
    TYPE = "type"
    SCREENSHOT = "screenshot"


@dataclass(frozen=True)
class ComputerRequest:
    action: ComputerAction
    target: str = ""
    text: str = ""


@dataclass(frozen=True)
class ComputerResult:
    action: ComputerAction
    success: bool
    evidence_ref: str


class ComputerAdapter(Protocol):
    def execute(self, request: ComputerRequest) -> ComputerResult: ...


class ComputerUsePolicy:
    """Default deny; explicit per-action allowlist and approval for writes."""

    def __init__(self, allowed_actions: frozenset[ComputerAction] = frozenset()):
        self.allowed_actions = allowed_actions

    def authorize(self, request: ComputerRequest, approved: bool = False) -> None:
        if request.action not in self.allowed_actions:
            raise PermissionError(f"Computer action not enabled: {request.action.value}")
        if request.action in (ComputerAction.CLICK, ComputerAction.TYPE) and not approved:
            raise PermissionError("Interactive computer action requires approval")


class ComputerUseService:
    def __init__(self, adapter: ComputerAdapter, policy: ComputerUsePolicy):
        self.adapter = adapter
        self.policy = policy

    def execute(self, request: ComputerRequest, approved: bool = False) -> ComputerResult:
        self.policy.authorize(request, approved=approved)
        result = self.adapter.execute(request)
        if not result.evidence_ref:
            raise RuntimeError("Computer use result lacks audit evidence")
        return result
