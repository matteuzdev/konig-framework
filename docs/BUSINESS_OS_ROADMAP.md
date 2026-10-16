# König Business OS — Frank-inspired expansion (Phase 1)

This is an original extension to KONIG, not a copy of Frank's private implementation.

## Preserve existing architecture
- ONIX remains the orchestrator; do not replace its engine.
- Preserve engineering squad, Waves/DAGs, SOPs, QA gates and SYNAPSE.
- Reuse existing marketing, sales and strategy squads.
- Add adapters for messaging, tools and UI rather than binding the core to a provider.

## Proposed operating flow
Goal → ONIX plan → DAG tasks → squad execution → evidence validation → human approval for sensitive actions → result timeline.

## Functional scope
1. Workspace/tenant boundaries, with isolated secrets and artifacts.
2. Agent roster and squad editor (engineering, marketing, sales, strategy; extensible).
3. Run timeline with queued/running/awaiting_approval/failed/completed.
4. Per-task verified evidence, logs, retries, cost and budget.
5. Draft-first integrations for landing pages, CRM, content and campaigns.
6. Telegram and WhatsApp adapters with authenticated identity mapping.
7. Optional web control center: queue, approvals, agent graph, traces, budget.

## Mandatory controls
- External publishing, customer messaging, payments and campaign spend require explicit approval.
- Never treat AST filtering or subprocess execution alone as a hardened security sandbox; production isolation needs OS/container boundaries, network egress policy and resource limits.
- Tenant-scoped authorization at every storage and tool boundary; audit approval actor and timestamp.
- Idempotency keys and retry limits for external actions.
- No fabricated metrics, deliverables, deployment URLs or completion statuses.

## Phase 1 code
`core/business/contracts.py` supplies dependency-free, in-memory task contracts and a fail-closed approval/evidence gate. It is not yet wired into the ONIX runtime or persistent storage.

## Acceptance criteria for subsequent phases
- Existing engineering workflow and tests remain unchanged.
- At least one business workflow executes end-to-end with real artifacts and recorded evidence.
- Cross-tenant access is rejected in API and storage tests.
- Approval blocks every externally consequential action.
- Dashboard displays persisted execution state rather than simulated agent activity.
