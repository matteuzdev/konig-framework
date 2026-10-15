"""Opt-in demo command for opening Deezer through König Computer Use.

Run on the user's own computer:
    python -m core.runtime.computer_use_demo deezer

The command opens a website only. Music playback remains a future integration.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from core.runtime.browser_adapter import BrowserOpenAdapter
from core.runtime.computer_use import (
    ComputerAction, ComputerRequest, ComputerUsePolicy, ComputerUseService,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="König Assistant: approved browser actions")
    parser.add_argument("destination", choices=["deezer"])
    args = parser.parse_args()
    urls = {"deezer": "https://www.deezer.com/"}
    url = urls[args.destination]
    adapter = BrowserOpenAdapter(
        audit_dir=Path.home() / ".konig" / "computer-use-audit",
        allowed_hosts=frozenset({"www.deezer.com"}),
    )
    service = ComputerUseService(
        adapter=adapter,
        policy=ComputerUsePolicy(frozenset({ComputerAction.OPEN_URL})),
    )
    result = service.execute(ComputerRequest(ComputerAction.OPEN_URL, url))
    print("Opened:" if result.success else "Browser did not confirm opening:", url)
    print("Audit:", result.evidence_ref)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
