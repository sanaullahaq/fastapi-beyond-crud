"""
0) What is conftest.py
   `conftest.py` is a pytest specific configuration file. We can put all our fixtures
   here and we do not need to import those fixture to use. Pytest will automatically
   look for those fixture into the `conftest.py` file. **`conftest.py` file must be
   inside the `tests` package.** All the subpackage(if we define) can also access this
   `conftest.py`

   however if we want we can define a separate `conftest.py` inside the subpackage
   of package `tests`. Then subpackage will use that `conftest.py`. And the upper level
   test modules/files will not have access to the `conftest.py` file inside the subpackage.

   Fixture meaning in general english - A "fixture" is any item or object that is permanently
   attached or firmly fixed in place. It most commonly refers to built-in household or
   business equipment (like lights, sinks, and plumbing), but can also describe a scheduled
   sporting event or a person who is constantly present in a specific place.

1) What is a fixture?
   A fixture is a pytest function that sets up and tears down the state needed by tests.
   Tests declare which fixtures they need via parameters (e.g. `def test_foo(session)`).
   Fixtures can yield a value for the test to use, and any code after `yield` runs as
   cleanup. They are modular, reusable, and can depend on other fixtures.

2) What is await session.flush()?
   session.flush() sends pending SQL statements (INSERT, UPDATE, DELETE) to the
   database WITHOUT committing the transaction. This makes auto-generated values
   like uid, created_at available via session.refresh(obj). It also surfaces
   constraint violations (unique, foreign key) immediately. The changes remain
   invisible to other transactions until commit(). In tests we flush instead of
   commit so the row exists within the same transaction and can be rolled back
   or truncated at cleanup.

3) What is @pytest.fixture vs @pytest_asyncio.fixture?
   @pytest.fixture     — for synchronous fixtures (def). Runs immediately.
   @pytest_asyncio.fixture — for asynchronous fixtures (async def). Wraps the
   coroutine so pytest's event loop can await it and inject the resolved value
   into the test. Without it, an async def fixture returns a coroutine object
   instead of the actual value.

4) Why we picked @pytest_asyncio.fixture?
   The project uses async SQLAlchemy (AsyncSession, asyncpg driver). All DB
   operations (flush, refresh, commit, exec) must be awaited. @pytest.fixture
   does not support await. @pytest_asyncio.fixture is the only way to make
   async fixtures work correctly. It also explicitly documents that the fixture
   performs async work, is config-independent (unlike asyncio_mode="auto"),
   and is the standard convention in the pytest-asyncio ecosystem.

5) How to run tests:

   pytest tests/ -v                           # run all tests, verbose
   pytest tests/test_auth/ -v                 # run auth tests only
   pytest tests/test_books/test_routes.py -v  # run a single file
   pytest tests/ -v -k "test_signup"          # run tests matching name
   pytest tests/ -v --tb=short                # short traceback on failure
   pytest tests/ -v --tb=long                 # full traceback
   pytest tests/ -x                           # stop on first failure
"""

import asyncio
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.__init__ import app
from src.db.main import get_session
from src.auth.utils import create_access_token, hash_password
from src.db.models import User


TEST_DATABASE_URL = "postgresql+asyncpg://sanaullahaq:12345@localhost:5432/bookly_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(test_engine):
    conn = await test_engine.connect()
    await conn.execute(
        text("TRUNCATE TABLE books, reviews, tags, booktag, users CASCADE")
    )
    await conn.commit()
    await conn.close()

    async with AsyncSession(bind=test_engine, expire_on_commit=False) as s:
        yield s


@pytest_asyncio.fixture
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    from src.middleware import limiter

    limiter._default_limits = []
    limiter._route_limits = {}
    limiter._dynamic_route_limits = {}
    limiter._application_limits = []
    limiter.__marked_for_limiting = {}

    from src.celery_tasks import send_email

    send_email.delay = lambda *args, **kwargs: None

    import src.auth.dependencies as auth_deps

    async def mock_token_in_blocklist(jti):
        return False

    async def mock_add_jti_to_blocklist(jti):
        pass

    auth_deps.token_in_blocklist = mock_token_in_blocklist
    import src.auth.routes as auth_routes

    auth_routes.add_jti_to_blocklist = mock_add_jti_to_blocklist

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(session):
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="user",
        is_verified=False,
        password_hash=hash_password("testpass123"),
    )  # type: ignore
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def verified_user(session):
    user = User(
        username="verifieduser",
        email="verified@example.com",
        first_name="Verified",
        last_name="User",
        role="user",
        is_verified=True,
        password_hash=hash_password("testpass123"),
    )  # type: ignore
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_token(verified_user):
    token = create_access_token(
        user_data={
            "email": verified_user.email,
            "user_uid": str(verified_user.uid),
        }
    )
    return token


@pytest_asyncio.fixture
async def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest_asyncio.fixture
async def admin_user(session):
    user = User(
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_verified=True,
        password_hash=hash_password("adminpass123"),
    )  # type: ignore
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user):
    token = create_access_token(
        user_data={
            "email": admin_user.email,
            "user_uid": str(admin_user.uid),
        }
    )
    return token


@pytest_asyncio.fixture
async def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
