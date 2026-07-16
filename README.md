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
В консоль дублируется информация вместе с подробными результатами всех прокси.
```
============================================================
socks4://67.231.23.67:4135
------------------------------------------------------------
  ✓  https://www.google.com               200    (1659 мс)
  ✓  https://www.cloudflare.com           200    (1993 мс)
  ✓  https://checkip.amazonaws.com        200    (2191 мс)


============================================================
socks4://61.25.210.123:4135
------------------------------------------------------------
  ✗  https://icanhazip.com                ОШИБКА (5537 мс): TimeoutError
  ✗  https://api.ipify.org                ОШИБКА (5536 мс): TimeoutError
  ✗  https://www.github.com               ОШИБКА (5536 мс): TimeoutError
```

## Настройки

Всё настраивается через аргументы командной строки:

```bash
uv run main.py --timeout 3 --concurrency 30 --sites-to-check 2 --proxies proxies.txt --output good.txt
```

| Аргумент             | По умолчанию       | Назначение                                    |
|----------------------|---------------------|------------------------------------------------|
| `--proxies`          | `proxies.txt`       | Файл со списком прокси                          |
| `--output`           | `good_proxies.txt`  | Файл для рабочих прокси                         |
| `--timeout`          | `5`                 | Таймаут запроса на сайт, сек.                   |
| `--sites-to-check`   | `3`                 | Сколько случайных сайтов проверять на прокси    |
| `--concurrency`      | `100`               | Сколько прокси проверять одновременно           |

Список проверяемых сайтов — `SITES` в `models.py`.

Справка по всем флагам:

```bash
uv run main.py --help
```