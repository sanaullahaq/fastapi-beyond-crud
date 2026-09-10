# SQLAlchemy / SQLModel Async Session Methods

Quick reference for `flush()`, `refresh()`, `commit()`, and `rollback()` on an
`AsyncSession`.

## `flush()`

Pushes pending changes to the DB **within the current transaction**, without
committing. Not durable yet — a later `rollback()` can still undo it. Useful
when you need a DB-generated value (like an autoincrement PK) before you're
ready to commit.

```python
book = Book(title="Dune", author="Herbert")
session.add(book)
await session.flush()
print(book.uid)   # PK now populated, but nothing durable yet
```

## `refresh(obj)`

Reloads an object's attributes straight from the DB, overwriting what's in
memory. Useful after `commit()` when you want DB-side defaults, triggers, or
`updated_at` timestamps.

```python
await session.commit()
await session.refresh(book)
print(book.created_at)   # DB-set default, now loaded into the object
```

## `commit()`

Flushes pending changes **and** ends the transaction, making them permanent.

```python
session.add(book)
await session.commit()   # row is now durable in Postgres
```

## `rollback()`

Discards everything pending in the current transaction; objects revert to
their last committed state (or vanish if they were never committed).

```python
try:
    session.add(book)
    await session.commit()
except Exception:
    await session.rollback()
    raise
```

## Note on this project

`async_session` in `src/db/main.py` is configured with
`expire_on_commit=False`. Normally SQLAlchemy expires all objects after
`commit()`, forcing a DB round-trip the next time you touch any attribute —
with that off, objects keep their in-memory values after commit instead. So
in this project, `refresh()` is really only needed when you specifically
want a value the DB computed (a default, a trigger, a generated timestamp)
that isn't already sitting in the object from before the commit.

## `expire_on_commit`, elaborated

`expire_on_commit` controls what happens to an object's **already-loaded**
attribute values the moment `commit()` succeeds.

**Default (`expire_on_commit=True`):** every object attached to the session
gets its attributes marked "expired" right after commit — not deleted, just
flagged stale. The next time you touch any attribute (`book.title`),
SQLAlchemy transparently fires a fresh `SELECT` to reload it, then hands you
the value. This guarantees you're always looking at what's actually in the
DB post-commit.

```python
async with async_session() as session:
    session.add(book)
    await session.commit()
    print(book.title)   # if expire_on_commit=True: triggers a hidden reload query here
```

Two problems come from this:

1. **Hidden extra queries.** Every attribute touch after a commit costs a
   round-trip, even when nothing changed.
2. **> It breaks entirely with `AsyncSession`.** A plain attribute access
   like `book.title` is a synchronous Python operation — there's no way for
   it to `await` an implicit reload. SQLAlchemy's async layer bridges
   sync-looking calls to real I/O using a greenlet trick, but that bridge is
   only active inside your `await session.execute(...)` calls, not around
   ordinary attribute access. So touching an expired attribute outside that
   context raises **`sqlalchemy.exc.MissingGreenlet`** (`"greenlet_spawn has
   not been called"`), not a quiet reload. If the session has already closed
   by the time you touch it, you'd instead get `DetachedInstanceError`.

That's why `expire_on_commit=False` isn't just a style preference for async
projects — it's close to mandatory. Your `src/db/main.py` sets it, which is
exactly why this works fine:

```python
session.add(book)
await session.commit()
print(book.title)   # expire_on_commit=False: just returns the in-memory value, no query
```

**With `expire_on_commit=False`:** nothing gets cleared. Objects keep
whatever values were in memory right before the commit. This is safe to do
outside an async context and safe even after the session closes — which
matters a lot in FastAPI, where a route often returns an ORM object and
FastAPI serializes it into the JSON response *after* your handler returns,
potentially after the session dependency has started tearing down.

**The tradeoff:** since nothing reloads automatically, if the DB computed
something you didn't already have in memory — a `server_default`, a
trigger, a generated column, an `onupdate` timestamp — your in-memory object
won't reflect it until you explicitly ask:

```python
await session.commit()
await session.refresh(book)   # explicit, safe to await, pulls current DB state
print(book.created_at)
```

`refresh()` works fine here because it's an explicit `await`-able call, not
an implicit side effect of attribute access.

One related thing worth knowing: `session.rollback()` always expires the
session's objects, regardless of `expire_on_commit`. That setting only
governs what happens after a *successful commit* — a rollback discards the
transaction, so SQLAlchemy expires everything unconditionally to avoid
leaving you holding values that were never actually persisted.


## Advantage of using AsyncSession

What `AsyncSession` is actually for: letting your database calls run
without blocking the event loop. In a FastAPI app built on `async def`
routes and `asyncpg`, every `await session.execute(...)` yields control
back to the event loop while Postgres is doing the work — so your app can
keep handling other incoming requests concurrently instead of sitting idle
waiting on that one query.

Contrast that with what happens if you used the plain sync `Session` (with
`psycopg2`, say) inside an `async def` route:

```python
async def get_book(book_id: int):
    result = session.execute(select(Book).where(Book.uid == book_id))  # sync, blocking
    ...
```

That call isn't a coroutine — it runs synchronously, in the same thread the
event loop is running on. While Postgres is thinking, your entire process
is frozen: no other request, no other coroutine, nothing runs until that
query returns. One slow query stalls every concurrent user of your app.
(FastAPI can dodge this by pushing plain `def` routes to a thread pool
automatically, but that pool is a fixed size — maybe 40 threads by default
— so you're back to being bounded, just with a bigger ceiling instead of
true async scalability.)

So the trade is: you give up two implicit conveniences designed for a
synchronous world, in exchange for requests not blocking each other on DB
I/O. For a project like yours — async routes, `asyncpg` driver, concurrent
request handling — that's a clearly worthwhile trade, and you're not even
paying the cost of it: `expire_on_commit=False` plus `lazy="selectin"`
already sidestep both cases where the implicit magic would've mattered.