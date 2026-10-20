"""Experimental bounded public-web extraction. Egress firewall required in production."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from urllib.parse import urlparse
import hashlib
import ipaddress
import socket
import httpx
from bs4 import BeautifulSoup

MAX_BYTES = 2_000_000

class PolicyError(ValueError): pass

def validate_url(url: str, *, allowed_hosts: tuple[str, ...] = ()) -> str:
    if not allowed_hosts:
        raise PolicyError("Explicit allowed_hosts required")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise PolicyError("Only absolute HTTP(S) URLs supported")
    if parsed.username or parsed.password or parsed.fragment:
        raise PolicyError("Credentials/fragments prohibited")
    if parsed.port not in (None, 80, 443):
        raise PolicyError("Unapproved port")
    host = parsed.hostname.lower().rstrip(".")
    if host not in {v.lower().rstrip(".") for v in allowed_hosts}:
        raise PolicyError("Host not allowed")
    if host in ("localhost", "localhost.localdomain") or host.endswith((".local", ".internal")):
        raise PolicyError("Private hostname")
    try:
        resolved = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, OSError) as exc:
        raise PolicyError("DNS failure") from exc
    if not resolved or any(not ipaddress.ip_address(v[4][0]).is_global for v in resolved):
        raise PolicyError("Non-global DNS address")
    return url

@dataclass(frozen=True)
class Evidence:
    source_url: str
    final_url: str
    fetched_at: str
    status: int
    title: str
    text: str
    sha256: str
    backend: str = "http-html"
    def json(self): return asdict(self)

def parse_html(url: str, raw: bytes, *, status=200) -> Evidence:
    if len(raw) > MAX_BYTES:
        raise PolicyError("Max response size exceeded")
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for element in soup(["script", "style", "noscript", "template", "nav", "footer"]):
        element.decompose()
    return Evidence(url, url, datetime.now(timezone.utc).isoformat(), status, title,
                    soup.get_text(" ", strip=True), hashlib.sha256(raw).hexdigest())

def extract(url: str, *, allowed_hosts: tuple[str, ...], timeout=12.0, transport=None) -> Evidence:
    validate_url(url, allowed_hosts=allowed_hosts)
    if not 0 < timeout <= 30:
        raise PolicyError("Invalid timeout")
    with httpx.Client(timeout=timeout, follow_redirects=False, trust_env=False,
                      transport=transport,
                      headers={"User-Agent": "KonigReach/0.2"}) as client:
        with client.stream("GET", url) as response:
            if 300 <= response.status_code < 400:
                raise PolicyError("Redirect blocked")
            response.raise_for_status()
            if "text/html" not in response.headers.get("content-type", "").lower():
                raise PolicyError("Unsupported content type")
            declared = response.headers.get("content-length", "")
            if declared.isdigit() and int(declared) > MAX_BYTES:
                raise PolicyError("Declared size too large")
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)
                if len(content) > MAX_BYTES:
                    raise PolicyError("Response too large")
            data = bytes(content)
            status = response.status_code
    return parse_html(url, data, status=status)
