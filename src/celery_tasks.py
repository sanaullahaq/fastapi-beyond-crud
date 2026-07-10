from asgiref.sync import async_to_sync
from celery import Celery

from src.mail import mail, create_mail_message


c_app = Celery()
c_app.config_from_object("src.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_mail_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message=message)
    # converting the async method into a sync method and calling it with (message=message). details are given below
    print("Email sent")
    r"""
    # `async_to_sync` comes from Django's `asgiref` library, but it's useful anywhere you need to call an async function from synchronous code — which is exactly the situation here.

    # **The problem it solves**

    # `mail.send_message` (from `fastapi_mail`) is an `async def` method. Normally you'd call it with `await mail.send_message(message)`, but `await` only works inside an `async def` function.

    # Celery tasks are synchronous by default — when Celery's worker picks up `send_email`, it just calls it like a regular function, not with `await`. So inside this task, you're in sync-land, but `mail.send_message` lives in async-land. You can't just do `mail.send_message(message)` — that would only return a coroutine object without actually running it, and you can't `await` it here since the task function itself isn't `async def`.

    # **What `async_to_sync` does**

    # `async_to_sync(mail.send_message)` wraps the async function and returns a new *synchronous* callable. That wrapper:

    # 1. Spins up (or reuses) an event loop
    # 2. Runs the coroutine `mail.send_message(message)` to completion on that loop
    # 3. Blocks the calling thread until it's done
    # 4. Returns the actual result (not a coroutine)

    # So `async_to_sync(mail.send_message)(message=message)` is roughly equivalent to:

    # ```python
    # import asyncio
    # asyncio.run(mail.send_message(message))
    # ```

    # Two-step breakdown:
    # ```python
    # sync_send = async_to_sync(mail.send_message)   # wrap: async fn -> sync fn
    # sync_send(message=message)                      # call it like a normal sync function
    # ```

    # **Why not just use `asyncio.run`?**

    # You could — `asyncio.run(mail.send_message(message))` would work almost the same way in this simple case. `async_to_sync` is more robust in trickier scenarios (e.g., nested event loops, threads that already have a running loop), which is why it's a common choice in mixed sync/async codebases like yours (FastAPI app + Celery worker). For a plain Celery task like this, either approach is fine — `async_to_sync` just happens to be a well-tested off-the-shelf tool for the job.

    # **Bottom line:** it lets your synchronous Celery task call an `async` `fastapi_mail` method without needing `async def`/`await`, by running the coroutine on a fresh event loop internally and waiting for it to finish before continuing to `print("Email sent")`.
    """

    r"""
    (env) sanaullahaq@HP:/mnt/Work/projects/fastapi/fastapi-beyond-crud$ celery -A src.celery_tasks.c_app worker --loglevel=INFO
    
    -------------- celery@HP v5.6.3 (recovery)
    --- ***** ----- 
    -- ******* ---- Linux-6.17.0-35-generic-x86_64-with-glibc2.39 2026-07-10 15:06:23
    - *** --- * --- 
    - ** ---------- [config]
    - ** ---------- .> app:         __main__:0x7cacb122a3f0
    - ** ---------- .> transport:   redis://localhost:6379/0
    - ** ---------- .> results:     redis://localhost:6379/0
    - *** --- * --- .> concurrency: 8 (prefork)
    -- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
    --- ***** ----- 
    -------------- [queues]
                    .> celery           exchange=celery(direct) key=celery
                    

    [tasks]
    . src.celery_tasks.send_email

    [2026-07-10 15:06:23,510: INFO/MainProcess] Connected to redis://localhost:6379/0
    [2026-07-10 15:06:23,512: INFO/MainProcess] mingle: searching for neighbors
    [2026-07-10 15:06:24,526: INFO/MainProcess] mingle: all alone
    [2026-07-10 15:06:24,553: INFO/MainProcess] celery@HP ready.
    """