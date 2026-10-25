"""Helper values and functions shared by the test modules (imported as `from api_helpers import ...`)."""
import os
import random
import uuid

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080").rstrip("/")
USERNAME = os.environ.get("API_USERNAME", "grader")
PASSWORD = os.environ.get("API_PASSWORD", "Library-Fall2026")
TIMEOUT = 10  # seconds; always pass timeout= so a dead server can't hang the run


def random_isbn():
    """13 random digits: unique enough that repeated test runs never collide."""
    return "".join(random.choice("0123456789") for _ in range(13))


def book_data(**overrides):
    """A valid book body with a unique author and isbn. Override any field."""
    data = {
        "title": "Integration Test Book",
        "author": f"Test Author {uuid.uuid4().hex[:8]}",
        "isbn": random_isbn(),
        "year": 2001,
    }
    data.update(overrides)
    return data
