from pathlib import Path
from typing import Optional

from models import ProxyResult, PROXY_PROTOCOLS


def output_proxy_result(result: ProxyResult):
    site = result.site_url
    if not result.working:
        print(f"  ✗  {site:<35}  {result.error}")
    else:
        print(f"  ✓  {site:<35}  {result.status_code}    ({result.time:.0f} мс)")


def get_proxies_from_files(path: Path) -> Optional[list[str]]:
    if not path.exists():
        path.touch()

    proxies = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(PROXY_PROTOCOLS):
                proxies.append(line)

    return proxies


def save_good_proxies(proxies: list[str], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(f"{proxy}\n" for proxy in proxies)