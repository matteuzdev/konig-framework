"""Business execution contracts for ONIX. No external side effects."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    FAILED = "failed"
    COMPLETED = "completed"

class ActionRisk(str, Enum):
    READ = "read"
    DRAFT = "draft"
    EXTERNAL_WRITE = "external_write"
    FINANCIAL = "financial"

@dataclass(frozen=True)
class Evidence:
    kind: str
    reference: str
    verified: bool = False

@dataclass
class BusinessTask:
    title: str
    squad: str
    tenant_id: str
    risk: ActionRisk = ActionRisk.DRAFT
    id: str = field(default_factory=lambda: str(uuid4()))
    status: RunStatus = RunStatus.QUEUED
    evidence: list[Evidence] = field(default_factory=list)
    approved_by: str | None = None
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def request_execution(self) -> RunStatus:
        if self.risk in (ActionRisk.EXTERNAL_WRITE, ActionRisk.FINANCIAL) and not self.approved_by:
            self.status = RunStatus.AWAITING_APPROVAL
        else:
            self.status = RunStatus.RUNNING
        return self.status

    def approve(self, actor: str, tenant_id: str) -> None:
        if tenant_id != self.tenant_id:
            raise PermissionError("Cross-tenant approval denied")
        if not actor.strip():
            raise ValueError("Approval requires an actor")
        self.approved_by = actor

    def complete(self) -> None:
        if self.status != RunStatus.RUNNING:
            raise ValueError("Task must be running")
        if not any(item.verified for item in self.evidence):
            raise ValueError("Verified evidence is required")
        self.status = RunStatus.COMPLETED
