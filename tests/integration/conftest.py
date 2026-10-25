"""Shared fixtures for the Library API integration tests.

Configuration comes from environment variables, so the same tests run against your
laptop, your EC2 server, a CI job, or the Gradescope autograder:

    BASE_URL      default http://127.0.0.1:8080   (no trailing /v1)
    API_USERNAME  default grader
    API_PASSWORD  default Library-Fall2026
"""
import time

import pytest
import requests

from api_helpers import BASE_URL, PASSWORD, TIMEOUT, USERNAME, book_data


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session", autouse=True)
def wait_for_service(base_url):
    """Poll /healthcheck until the server answers (a freshly booted EC2 instance can take a minute)."""
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            if requests.get(f"{base_url}/healthcheck", timeout=5).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(3)
    pytest.fail(f"{base_url}/healthcheck did not return 200 within 120 seconds")


@pytest.fixture(scope="session")
def credentials():
    return {"username": USERNAME, "password": PASSWORD}


@pytest.fixture(scope="session")
def auth_token(base_url, credentials):
    r = requests.post(f"{base_url}/v1/login", json=credentials, timeout=TIMEOUT)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def make_book(base_url, auth_headers):
    """Factory fixture: make_book(**overrides) creates a book and returns the response JSON.
    Every book it creates is returned (if checked out) and deleted after the test."""
    created = []

    def _make(**overrides):
        r = requests.post(f"{base_url}/v1/books", json=book_data(**overrides),
                          headers=auth_headers, timeout=TIMEOUT)
        assert r.status_code == 201, f"setup: could not create book: {r.status_code} {r.text}"
        book = r.json()
        created.append(book["id"])
        return book

    yield _make
    for book_id in created:
        requests.post(f"{base_url}/v1/books/{book_id}/return", headers=auth_headers, timeout=TIMEOUT)
        requests.delete(f"{base_url}/v1/books/{book_id}", headers=auth_headers, timeout=TIMEOUT)
