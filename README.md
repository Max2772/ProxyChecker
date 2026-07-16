# ProxyChecker

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![asyncio](https://img.shields.io/badge/async-aiohttp-informational)
![Proxy](https://img.shields.io/badge/proxy-HTTP%20%7C%20SOCKS4%20%7C%20SOCKS5-success)

Простой асинхронный чекер прокси (HTTP/HTTPS/SOCKS4/SOCKS5) — проверяет список прокси из файла (`proxies.txt`) на нескольких случайных сайтах и сохраняет рабочие в `good_proxies.txt`.

## Установка

```bash
uv sync
```

## Использование

Добавьте прокси в `proxies.txt` (по одному на строку, с префиксом схемы):

```
socks5://1.2.3.4:1080
socks5://user:pass@1.2.3.4:1080
http://5.6.7.8:8080
```

Запуск:

```bash
uv run main.py
```

Прокси, прошедший все проверки, попадает в `good_proxies.txt` (перезаписывается при каждом запуске).

## Настройки

Константы в начале `main.py`:

- `TIMEOUT` — таймаут запроса на сайт, сек.
- `SITES_TO_CHECK` — сколько случайных сайтов из `models.SITES` проверять на прокси.
- `CONCURRENCY` — сколько прокси проверять одновременно.
- `PROXIES_PATH` — путь файла исходных прокси.
- `GOOD_PROXIES_PATH` — путь файла рабочих прокси.
- `SITES` (models.py) — список сайтов для проверки.