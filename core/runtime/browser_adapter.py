"""Local browser adapter for the opt-in König Assistant Computer Use service.

Only opens HTTPS URLs in the user's default browser. It does not grant
screen control, shell access, credential access, or unattended clicking.
"""
from __future__ import annotations

import ipaddress
import json
from pathlib import Path
import socket
import time
from urllib.parse import urlsplit
import uuid
import webbrowser

from core.runtime.computer_use import ComputerAction, ComputerRequest, ComputerResult


class BrowserOpenAdapter:
    def __init__(self, audit_dir: str | Path, allowed_hosts: frozenset[str]):
        self.audit_dir = Path(audit_dir)
        self.allowed_hosts = frozenset(host.lower() for host in allowed_hosts)

    def execute(self, request: ComputerRequest) -> ComputerResult:
        if request.action is not ComputerAction.OPEN_URL:
            raise PermissionError("Browser adapter supports OPEN_URL only")
        url = urlsplit(request.target)
        host = (url.hostname or "").lower()
        if url.scheme != "https" or not host or host not in self.allowed_hosts:
            raise PermissionError("Only allowlisted HTTPS domains may be opened")
        if url.username or url.password or url.port not in (None, 443):
            raise PermissionError("Credentials and nonstandard ports are forbidden")
        if request.text:
            raise ValueError("OPEN_URL does not accept text payloads")

        # Domain allowlisting alone is insufficient: block loopback/private DNS targets.
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        if not addresses:
            raise PermissionError("Host cannot be resolved")
        for item in addresses:
            ip = ipaddress.ip_address(item[4][0])
            if not ip.is_global:
                raise PermissionError("Private or local address is forbidden")

        opened = bool(webbrowser.open(request.target, new=2))
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        audit_id = uuid.uuid4().hex
        audit_file = self.audit_dir / (audit_id + ".json")
        audit_file.write_text(
            json.dumps({
                "id": audit_id,
                "timestamp": time.time(),
                "action": request.action.value,
                "host": host,
                "success": opened,
            }),
            encoding="utf-8",
        )
        return ComputerResult(
            action=request.action,
            success=opened,
            evidence_ref=str(audit_file),
        )
