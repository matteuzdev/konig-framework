"""Pluggable extraction interfaces; no upstream tool installed or bypassed."""
from dataclasses import dataclass
from typing import Callable
from .core import Evidence, PolicyError, parse_html, validate_url

@dataclass(frozen=True)
class AdapterSpec:
    name: str
    purpose: str
    readiness: str

ADAPTERS = (
    AdapterSpec("http-html", "Public static HTML", "implemented-offline-tested"),
    AdapterSpec("scrapling", "Authorized optional HTML fetcher", "integration-boundary"),
    AdapterSpec("agent-reach", "Platform connectors through approved interface", "design-only"),
    AdapterSpec("browser", "Isolated authorized browser extraction", "design-only"),
)

def list_capabilities():
    return [vars(spec).copy() for spec in ADAPTERS]

def scrapling_extract(url: str, *, allowed_hosts: tuple[str, ...], fetcher: Callable[[str], bytes]) -> Evidence:
    """Caller-supplied trusted fetcher; isolation/egress controls remain required."""
    validate_url(url, allowed_hosts=allowed_hosts)
    raw = fetcher(url)
    if not isinstance(raw, bytes):
        raise PolicyError("Fetcher must return bytes")
    record = parse_html(url, raw)
    return Evidence(**{**record.json(), "backend": "scrapling-adapter"})
