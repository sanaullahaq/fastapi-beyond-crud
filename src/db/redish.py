import redis.asyncio as aioredis
from src.config import Config


token_blocklist = aioredis.from_url(Config.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=Config.JTI_EXPIRY_SECONDS)
    # "Remember that this jti is blocked, but forget it automatically in JTI_EXPIRY_SECONDS (1 hour)."


async def token_in_blocklist(jti: str) -> bool:
    value = await token_blocklist.get(jti)
    return value is not None

# GET jti returns the stored value ("") if the key exists, or None if it doesn't (either never blocked, or expired).
# value is not None → True means "this jti is in the blocklist" (i.e., blocked/revoked).
