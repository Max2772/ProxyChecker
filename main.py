import asyncio
import random
import time
from pathlib import Path

import aiohttp
from aiohttp_socks import ProxyConnector

from utils import output_proxy_result, get_proxies_from_files, save_good_proxies
from models import ProxyResult, SITES, USER_AGENT

GOOD_PROXIES: set[str] = set()
BAD_PROXIES: set[str] = set()

PROXIES_PATH: Path = Path("proxies.txt")
GOOD_PROXIES_PATH: Path = Path("good_proxies.txt")

TIMEOUT: float = 5
SITES_TO_CHECK: int = 3


async def check_proxy(site_url: str, proxy_url: str) -> ProxyResult:
    start = time.perf_counter()
    try:
        connector = ProxyConnector.from_url(proxy_url)
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        headers = {"User-Agent": USER_AGENT}
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
            async with session.get(site_url, ssl=False) as r:
                dt = (time.perf_counter() - start) * 1000
                working = r.status < 400
                return ProxyResult(
                    proxy_url=proxy_url,
                    site_url=site_url,
                    working=working,
                    status_code=r.status,
                    time=dt,
                    error=None if working else f"HTTP {r.status}"
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


async def main():
    proxies = get_proxies_from_files(PROXIES_PATH)

    if not proxies:
        print(f"Не найдены прокси. Добавьте их в {PROXIES_PATH}")
        return

    tasks = []
    for proxy in proxies:
        sites = random.sample(SITES, SITES_TO_CHECK)
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

        if not result.working:
            BAD_PROXIES.add(result.proxy_url)
        if result.working and result.proxy_url not in BAD_PROXIES:
            GOOD_PROXIES.add(result.proxy_url)

        last_proxy = result.proxy_url

    print(f"\n{len(GOOD_PROXIES)} рабочих прокси:")
    for proxy in GOOD_PROXIES:
        print(proxy)

    print(f"\n{len(BAD_PROXIES)} нерабочих прокси:")
    for proxy in BAD_PROXIES:
        print(proxy)

    save_good_proxies(list(GOOD_PROXIES), GOOD_PROXIES_PATH)

if __name__ == "__main__":
    asyncio.run(main())