import requests

from api_helpers import TIMEOUT


def test_healthcheck_returns_ok(base_url):
    r = requests.get(f"{base_url}/healthcheck", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    assert r.json() == {"status": "ok"}
