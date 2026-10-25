"""Example: using the make_book fixture to create the data a test needs.

make_book() creates a book on the server and returns it as JSON. Every book it creates is
deleted after the test, so each test starts from its own fresh data.
"""
import requests

from api_helpers import TIMEOUT


def test_get_book_returns_created_book(base_url, auth_headers, make_book):
    book = make_book()  # one new book with a unique author and ISBN
    r = requests.get(f"{base_url}/v1/books/{book['id']}", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json() == book
