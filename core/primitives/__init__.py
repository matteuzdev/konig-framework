"""
Konig Primitives — As abstrações fundamentais do framework KONIG.
"""

from core.primitives.message import KonigMessage, MessageType
from core.primitives.handoff import KonigHandoff
from core.primitives.skill import KonigSkill, SkillTier, SkillCategory, SkillInput, SkillOutput
from core.primitives.gate import KonigGate, GateResult, GateVerdict
from core.primitives.task import KonigTask, TaskStatus, TaskPriority, TaskOutput
from core.primitives.workflow import KonigWorkflow, WorkflowStatus

__all__ = [
    "KonigMessage",
    "MessageType",
    "KonigHandoff",
    "KonigSkill",
    "SkillTier",
    "SkillCategory",
    "SkillInput",
    "SkillOutput",
    "KonigGate",
    "GateResult",
    "GateVerdict",
    "KonigTask",
    "TaskStatus",
    "TaskPriority",
    "TaskOutput",
    "KonigWorkflow",
    "WorkflowStatus",
]
