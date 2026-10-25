# Library API Specification (v1)

This document is the contract for the Book Lending Library API. Your server must implement it exactly: the autograder checks your deployed server against this document, and your integration tests should check it too.

## General Rules

| Rule | Value |
|---|---|
| Port | `8080` |
| Base URL | `http://<host>:8080` (paths below are relative to this) |
| Request and response format | JSON, with header `Content-Type: application/json` on every response that has a body |
| Authentication | Bearer token: `Authorization: Bearer <access_token>` |
| Error responses | Every `4xx` response has a JSON body of the form `{"error": "<human-readable message>"}` |
| Unknown paths | `404 Not Found` |

### Grading Account

Your server must accept this fixed user. The autograder logs in with it.

| Field | Value |
|---|---|
| `username` | `grader` |
| `password` | `Library-Fall2026` |

### Authentication

Every path under `/v1/` **except** `POST /v1/login` requires a valid bearer token. A request with a missing, malformed, or unknown token returns `401 Unauthorized`. Tokens must stay valid for as long as the server process is running.

---

## The Book Resource

```json
{
  "id": 7,
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt",
  "isbn": "9780135957059",
  "year": 2019,
  "available": true
}
```

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Assigned by the server. Never reused. |
| `title` | string | Required. 1–200 characters after trimming whitespace. |
| `author` | string | Required. 1–200 characters after trimming whitespace. |
| `isbn` | string | Required. Exactly 10 or 13 digits (`0`–`9`), no hyphens or spaces. **Unique** across all books. |
| `year` | integer | Required. A JSON integer (not a string, not a boolean) from `1450` to `2100` inclusive. |
| `available` | boolean | Set by the server. `true` when created; changed only by checkout and return. Ignored if sent in a request body. |

A request body that is not valid JSON, or is not a JSON object, returns `400 Bad Request`.

---

## Endpoints

### `GET /healthcheck`

No authentication.

**200 OK**

```json
{"status": "ok"}
```

### `POST /v1/login`

No authentication.

Request body:

```json
{"username": "grader", "password": "Library-Fall2026"}
```

| Result | Status | Body |
|---|---|---|
| Correct credentials | `200 OK` | `{"access_token": "<string>", "token_type": "Bearer"}` |
| Wrong username or password | `401 Unauthorized` | error body |
| Missing `username` or `password`, or invalid JSON | `400 Bad Request` | error body |

### `GET /v1/books`

Lists books in ascending `id` order.

Query parameters (all optional):

| Parameter | Default | Rules |
|---|---|---|
| `page` | `1` | Integer, `>= 1` |
| `page_size` | `10` | Integer, `1`–`50` |
| `author` | none | Exact match on `author`, **case-insensitive** |
| `available` | none | `true` or `false` |

Any invalid query parameter value returns `400 Bad Request`.

**200 OK**

```json
{
  "books": [ { "...": "book objects" } ],
  "pagination": {
    "page": 2,
    "page_size": 3,
    "total": 8,
    "pages": 3,
    "has_next": true,
    "has_prev": true
  }
}
```

| Field | Meaning |
|---|---|
| `total` | Number of books matching the filters, across **all** pages |
| `pages` | `ceil(total / page_size)`; `0` when `total` is `0` |
| `has_next` | `page < pages` |
| `has_prev` | `page > 1` |

A `page` past the last page returns `200 OK` with an empty `books` list.

### `POST /v1/books`

Creates a book. Request body: `title`, `author`, `isbn`, `year`.

| Result | Status | Body |
|---|---|---|
| Created | `201 Created`, with header `Location: /v1/books/<id>` | the new book |
| Missing or invalid field | `400 Bad Request` | error body |
| `isbn` already used by another book | `409 Conflict` | error body |

### `GET /v1/books/{id}`

| Result | Status | Body |
|---|---|---|
| Found | `200 OK` | the book |
| No book with that `id` (including a non-integer `id`) | `404 Not Found` | error body |

### `PUT /v1/books/{id}`

Replaces `title`, `author`, `isbn`, and `year`. All four are required and follow the same rules as `POST`. `available` is not changed.

| Result | Status | Body |
|---|---|---|
| Updated | `200 OK` | the updated book |
| No book with that `id` | `404 Not Found` | error body |
| Missing or invalid field | `400 Bad Request` | error body |
| `isbn` already used by a *different* book | `409 Conflict` | error body |

If the book doesn't exist, return `404` without checking the body.

### `DELETE /v1/books/{id}`

| Result | Status | Body |
|---|---|---|
| Deleted | `204 No Content` | none |
| No book with that `id` | `404 Not Found` | error body |
| Book is checked out (`available` is `false`) | `409 Conflict` | error body |

### `POST /v1/books/{id}/checkout`

| Result | Status | Body |
|---|---|---|
| Checked out | `200 OK` | the book, with `available: false` |
| Already checked out | `409 Conflict` | error body |
| No book with that `id` | `404 Not Found` | error body |

### `POST /v1/books/{id}/return`

| Result | Status | Body |
|---|---|---|
| Returned | `200 OK` | the book, with `available: true` |
| Not checked out | `409 Conflict` | error body |
| No book with that `id` | `404 Not Found` | error body |

---

## Order of Checks

When more than one error applies, return the first one that matches in this order:

1. `401`: authentication
2. `404`: the book in the path doesn't exist
3. `400`: the request body or query string is invalid
4. `409`: the request conflicts with the current state
