from urllib.request import urlopen


with urlopen("http://localhost:8000/health", timeout=2) as response:
    if response.status != 200:
        raise SystemExit(1)
