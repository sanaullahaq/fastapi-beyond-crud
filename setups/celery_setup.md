FastAPI's background tasks are a convenient way to handle asynchronous operations without blocking the main thread. However, as the number of background tasks increases, running them all on the same FastAPI server can lead to performance bottlenecks. To address this, we can use Celery, a more scalable solution that allows tasks to be distributed across multiple worker processes and servers. This helps manage high loads efficiently and ensures that your application remains responsive even when handling a large number of background tasks.

# Celery Setup Guide

## 1. Install dependencies

```bash
pip install celery[redis] asgiref flower
```

- `celery[redis]` — Celery with Redis as the message broker
- `asgiref` — `async_to_sync` to call async functions from sync Celery tasks
- `flower` — web-based monitoring UI (optional)

## 2. Create the Celery app (`src/celery_tasks.py`)

```python
from asgiref.sync import async_to_sync
from celery import Celery

from src.mail import mail, create_mail_message

c_app = Celery()
c_app.config_from_object("src.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_mail_message(recipients=recipients, subject=subject, body=body)
    async_to_sync(mail.send_message)(message=message)
    print("Email sent")
```

## 3. Add Celery config (`src/config.py`)

At the bottom of `src/config.py` (after the `Config = Settings()` line):

```python
# Celery Configuration
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
```

Celery reads these as module-level variables on the `Settings` class when `config_from_object("src.config")` is called.

## 4. Queue a task — `.delay()`

```python
from src.celery_tasks import send_email

task = send_email.delay(
    ["user@example.com"],
    "Verify your email",
    "<h1>Click the link to verify</h1>"
)
print(task.id)      # UUID of the task
print(task.status)  # PENDING → SUCCESS (once worker picks it up)
```

## 5. Start the worker (separate terminal)

```bash
celery -A src.celery_tasks.c_app worker --loglevel=INFO
```

Keep this terminal running. The worker polls Redis for queued tasks and executes them.

## 6. Monitor with Flower (separate terminal, optional)

```bash
celery -A src.celery_tasks.c_app flower
```

Opens a web UI at `http://localhost:5555` — view task status, retry failed tasks, inspect queues.

## Architecture

```
┌──────────────────────┐   .delay()    ┌──────────┐    consume    ┌──────────────────┐
│  FastAPI endpoint    │ ───────────►  │  Redis   │ ◄───────────  │  Celery Worker   │
│  (producer)          │               │ (broker) │               │  (separate proc) │
└──────────────────────┘               └──────────┘               └──────────────────┘
                                                                   celery -A src.celery_tasks.c_app worker
```

**Key rule:** The worker must be running **before** or **independently of** `.delay()` calls — it is always a separate process.
