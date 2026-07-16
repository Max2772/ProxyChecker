from dataclasses import dataclass
from typing import Optional


PROXY_PROTOCOLS = ("http://", "https://", "socks4://", "socks5://", "socks5h://")

SITES = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://www.github.com",
    "https://httpbin.org/ip",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

@dataclass(slots=True)
class ProxyResult:
    proxy_url: str
    site_url: str
    working: bool
    status_code: Optional[int]
    time: float
    error: Optional[str] = None


