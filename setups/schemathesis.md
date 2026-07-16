# Schemathesis — Automated API Testing

## 1. Install

```bash
pip install schemathesis
```

## 2. Start the server

```bash
uvicorn src.__init__:app
Or
fastapi dev src/
```

## 3. Basic scan (runs all endpoints at once)

```bash
st run http://127.0.0.1:8000/api/v1/openapi.json
```

This generates and runs hundreds of test cases against every endpoint — overwhelming for debugging.

## 4. Run tests one at a time

### 4a. Target a single endpoint

```bash
st run --endpoint /api/v1/books \
  http://127.0.0.1:8000/api/v1/openapi.json
```

### 4b. Target a single method on an endpoint

```bash
st run --endpoint /api/v1/books --method POST \
  http://127.0.0.1:8000/api/v1/openapi.json
```

### 4c. Minimise generated examples

```bash
st run --hypothesis-max-examples=1 \
  --endpoint /api/v1/books \
  http://127.0.0.1:8000/api/v1/openapi.json
```

Without this, Hypothesis generates up to 100 examples per endpoint by default.

### 4d. Dry-run (list tests without executing)

```bash
st run --dry-run http://127.0.0.1:8000/api/v1/openapi.json
```

Useful for seeing what tests exist before running them.

## 5. Authentication

Most endpoints require a Bearer token. Pass it via `--header`:

```bash
st run --header "Authorization: Bearer <your_token>" \
  http://127.0.0.1:8000/api/v1/openapi.json
```

To get a token, either:

- Call `/api/v1/auth/signup` then `/api/v1/auth/login`
- Or insert a test user directly into the database

## 6. Useful flags

| Flag | Purpose |
|---|---|
| `--endpoint /path` | Test only specific paths |
| `--method GET,POST` | Filter by HTTP method |
| `--hypothesis-max-examples=N` | Limit test cases per endpoint (default: 100) |
| `--checks all` | Run all built-in checks |
| `--stateful=links` | Follow API links (create → get → update → delete) |
| `--workers N` | Parallel execution |
| `--dry-run` | List tests without running them |
| `-v` | Verbose output |
| `--header "Key: Value"` | Add custom headers |

## 7. Pytest integration (recommended)

Schemathesis registers each generated case as a separate pytest test. Create `tests/test_api.py`:

```python
import schemathesis

schema = schemathesis.from_url("http://127.0.0.1:8000/api/v1/openapi.json")
TOKEN = "<your_token>"


@schema.hook
def before_generate_case(context, strategy):
    # Skip auth endpoints that have their own auth requirements
    pass


@schema.parametrize()
def test_api(case):
    # Inject auth header for protected endpoints
    if "/api/v1/auth/" not in case.operation.definition.path:
        case.headers["Authorization"] = f"Bearer {TOKEN}"
    case.call_and_validate()
```

Then filter individual tests with `-k`:

```bash
pytest -v -k "POST and /api/v1/books"       # only POST tests on books
pytest -v -k "GET and /api/v1/reviews"      # only GET on reviews
pytest -v -k "status_200"                    # only tests expecting 200
pytest -v -k "not POST"                      # all methods except POST
```

## 8. Testing auth-protected endpoints without a real token

For endpoints that need authentication, you can use a Schemathesis **hook** to intercept and inject a valid token before each request:

```python
import schemathesis

schema = schemathesis.from_url("http://127.0.0.1:8000/api/v1/openapi.json")


def get_test_token() -> str:
    """Obtain a fresh token for testing."""
    # Option 1: Return a hardcoded token for dev
    # Option 2: Call signup + login endpoints programmatically
    # Option 3: Create a test user and generate a token
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."


@schema.parametrize()
def test_api(case):
    # Public auth endpoints don't need a token
    public_paths = ["/api/v1/auth/signup", "/api/v1/auth/login"]
    if case.operation.definition.path not in public_paths:
        case.headers["Authorization"] = f"Bearer {get_test_token()}"
    case.call_and_validate()
```

## 9. Practical workflow for this codebase

```bash
# 1. Start server
uvicorn src.__init__:app &

# 2. Test a single POST on books with 1 example
st run --endpoint /api/v1/books --method POST \
  --hypothesis-max-examples=1 \
  --header "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/openapi.json

# 3. Test a single GET on reviews
st run --endpoint /api/v1/reviews --method GET \
  --hypothesis-max-examples=1 \
  --header "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/openapi.json

# 4. Full scan with all checks (slow - runs hundreds of tests)
st run --checks all \
  --header "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/openapi.json
```
