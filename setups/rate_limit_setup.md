# Rate Limiting Setup Guide

## 1. Install dependency

```bash
pip install slowapi
```

## 2. Configure the limiter (`src/middleware.py`)

Add a module-level `limiter` instance and a registration function:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.config import Config

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.REDIS_URL,
    default_limits=["5/minute"],
)

def register_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

- `key_func=get_remote_address` — identifies clients by IP address
- `storage_uri=Config.REDIS_URL` — uses the existing Redis for tracking counts
- `default_limits=["5/minute"]` — fallback for endpoints without an explicit limit

### Available `key_func` options

SlowAPI provides two built-in key functions:

| Function              | Source                    | Use when                                      |
|-----------------------|---                        |---                                            |
| `get_remote_address`  | `request.client.host`     | Direct client connections (no proxy)          |
| `get_ipaddr`          | `X-Forwarded-For` header  | Behind a reverse proxy (Nginx, Render, etc.)  |

You can also pass a **custom callable** — it just needs to accept `Request` and return a string:

```python
# Rate limit by authenticated user ID instead of IP
def get_user_id(request: Request) -> str:
    return request.state.token_data.get("user", {}).get("user_uid", get_remote_address(request))

limiter = Limiter(key_func=get_user_id, ...)
```

This is useful for auth-protected endpoints — rate limiting by IP is meaningless when all users come from the same corporate NAT.

## 3. Register in the app factory (`src/__init__.py`)

```python
from src.middleware import register_rate_limiter

register_rate_limiter(app)
```

## 4. Apply to endpoints

Import the `limiter` and decorate the route with `@limiter.limit(...)`. The route **must** accept a `request: Request` parameter for slowapi to extract the client IP. It doesn't affect existing logic.

```python
from fastapi import Request
from src.middleware import limiter

@auth_router.post("/password-reset-request")
@limiter.limit("3/hour")
async def password_reset_request(
    email_data: PasswordResetRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    ...
```

## 5. Suggested rate limits

| Endpoint | Limit | Rationale |
|---|---|---|
| `POST /password-reset-request`    | `3/hour`      | Prevent email flooding        |
| `POST /login`                     | `10/minute`   | Brute-force protection        |
| `POST /signup`                    | `5/hour`      | Prevent account creation spam |
| `POST /send_mail`                 | `5/hour`      | Email abuse prevention        |

## 6. Response on rate limit exceeded

Returns HTTP **429 Too Many Requests**:

```json
{
  "detail": "Rate limit exceeded: 3 per 1 hour"
}
```

## Architecture

```
Request ──► SlowAPI middleware ──► Redis key "rate:{ip}:{endpoint}"
                │
     ┌──────────┴──────────┐
     │ count < limit?      │
     └──────┬──────┬───────┘
        Yes │      │ No
            v      v
     Forward to    Return 429
     route handler Too Many Requests
```
