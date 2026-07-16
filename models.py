from dataclasses import dataclass
from typing import Optional


PROXY_PROTOCOLS = ("http://", "https://", "socks4://", "socks5://", "socks5h://")

SITES = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://www.github.com",
    "https://www.cloudflare.com",
    "https://httpbin.org/ip",
]

@dataclass(slots=True)
class ProxyResult:
    proxy_url: str
    site_url: str
    working: bool
    status_code: Optional[int]
    time: float
    error: Optional[str] = None


