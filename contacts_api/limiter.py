
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings

async def setup_limiter():
    """
    The setup_limiter function is used to initialize the FastAPILimiter library.
    It takes no arguments, and returns nothing. It must be called before any other
    FastAPILimiter functions are called.
    
    :return: The fastapilimiter object
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)