import asyncio
import random
import time
from pathlib import Path

import aiohttp
from aiohttp_socks import ProxyConnector

from models import ProxyResult, PROXY_PROTOCOLS, SITES


PROXIES: list[str] = []
GOOD_PROXIES: list[ProxyResult] = []
BAD_PROXIES: list[ProxyResult] = []

TIMEOUT: float = 5
SITES_TO_CHECK: int = 3


def get_proxies_from_files(file: str = "proxies.txt"):
    path = Path(file)

    if not path.exists():
        path.touch()
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(PROXY_PROTOCOLS):
                PROXIES.append(line)


async def check_proxy(site_url: str, proxy_url: str) -> ProxyResult:
    start = time.perf_counter()
    try:
        connector = ProxyConnector.from_url(proxy_url)
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(site_url, ssl=False) as r:
                dt = (time.perf_counter() - start) * 1000
                return ProxyResult(
                    proxy_url=proxy_url,
                    site_url=site_url,
                    working=True,
                    status_code=r.status,
                    time=dt
                )

    except Exception as e:
        dt = (time.perf_counter() - start) * 1000
        return ProxyResult(
            proxy_url=proxy_url,
            site_url=site_url,
            working=False,
            status_code=None,
            time=dt,
            error=f"ОШИБКА ({dt:.0f} мс): {type(e).__name__}"
        )


def output_proxy_result(result: ProxyResult):
    site = result.site_url
    if not result.working:
        print(f"  ✗  {site:<35}  {result.error}")
    else:
        print(f"  ✓  {site:<35}  {result.status_code}    ({result.time:.0f} мс)")


async def main():
    get_proxies_from_files()

    tasks = []
    for proxy in PROXIES:
        sites = random.sample(SITES, 2)
        for site in sites:
            tasks.append(check_proxy(proxy_url=proxy, site_url=site))

    results = await asyncio.gather(*tasks)
    proxy_results = sorted(results, key=lambda proxy: (proxy.proxy_url, proxy.working))

    last_proxy = None
    
    for result in proxy_results:
        if result.proxy_url != last_proxy:
            print("\n")
            print("=" * 60)
            print(result.proxy_url)
            print("-" * 60)

        output_proxy_result(result)

        if not result.working and result.proxy_url:
            BAD_PROXIES.append(result)

        if result.working and result.proxy_url in BAD_PROXIES:
            BAD_PROXIES.append(result)

        if result.working and result.proxy_url not in BAD_PROXIES:
            GOOD_PROXIES.append(result)

        last_proxy = result.proxy_url


    print("\nСписок рабочих прокси:")
    for proxy in GOOD_PROXIES:
        print(proxy.proxy_url)

    print("\nСписок нерабочих прокси:")
    for proxy in BAD_PROXIES:
        print(proxy.proxy_url)

if __name__ == "__main__":
    asyncio.run(main())