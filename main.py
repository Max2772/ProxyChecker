import argparse
import asyncio
import random
import time
from collections import defaultdict
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
CONCURRENCY: int = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Асинхронный чекер прокси")
    parser.add_argument("--proxies", type=Path, default=PROXIES_PATH, help="Файл со списком прокси")
    parser.add_argument("--output", type=Path, default=GOOD_PROXIES_PATH, help="Файл для рабочих прокси")
    parser.add_argument("--timeout", type=float, default=TIMEOUT, help="Таймаут запроса, сек")
    parser.add_argument("--sites-to-check", type=int, default=SITES_TO_CHECK, help="Сколько сайтов проверять на каждом прокси")
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY, help="Сколько прокси проверять одновременно")
    return parser.parse_args()


async def check_proxy(site_url: str, proxy_url: str, semaphore: asyncio.Semaphore, timeout: float) -> ProxyResult:
    start = time.perf_counter()
    try:
        async with semaphore:
            connector = ProxyConnector.from_url(proxy_url)
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            headers = {"User-Agent": USER_AGENT}
            async with aiohttp.ClientSession(connector=connector, timeout=client_timeout, headers=headers) as session:
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
    args = parse_args()
    proxies = get_proxies_from_files(args.proxies)

    if not proxies:
        print(f"Не найдены прокси. Добавьте их в {args.proxies}")
        return

    semaphore = asyncio.Semaphore(args.concurrency)

    tasks = []
    for proxy in proxies:
        sites = random.sample(SITES, args.sites_to_check)
        for site in sites:
            tasks.append(check_proxy(proxy_url=proxy, site_url=site, semaphore=semaphore, timeout=args.timeout))

    results = await asyncio.gather(*tasks)
    results_by_proxy: dict[str, list[ProxyResult]] = defaultdict(list)

    for result in results:
        results_by_proxy[result.proxy_url].append(result)

    for proxy_url in sorted(results_by_proxy):
        print("\n")
        print("=" * 60)
        print(proxy_url)
        print("-" * 60)

        for result in results_by_proxy[proxy_url]:
            output_proxy_result(result)

        if all(result.working for result in results_by_proxy[proxy_url]):
            GOOD_PROXIES.add(proxy_url)
        else:
            BAD_PROXIES.add(proxy_url)

    print(f"\n{len(GOOD_PROXIES)} рабочих прокси:")
    for proxy in GOOD_PROXIES:
        print(proxy)

    print(f"\n{len(BAD_PROXIES)} нерабочих прокси:")
    for proxy in BAD_PROXIES:
        print(proxy)

    save_good_proxies(list(GOOD_PROXIES), args.output)

if __name__ == "__main__":
    asyncio.run(main())