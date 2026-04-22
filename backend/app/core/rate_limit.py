"""Rate limiting dependency using Redis."""

import time
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.core.cache import get_cache_client
from app.core.config import settings


class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self, req: Request):
        # Identify requester (IP or User ID)
        identifier = req.client.host if req.client else "unknown"
        if hasattr(req.state, "user_id") and req.state.user_id:
            identifier = str(req.state.user_id)
            
        key = f"rate_limit:{req.url.path}:{identifier}"
        cache = await get_cache_client()
        
        # Simple window-based rate limiting
        current = await cache.get(key)
        if current is not None and int(current) >= self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )
            
        async with cache.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, self.seconds)
            await pipe.execute()


# Predefined limiters
auth_rate_limit = RateLimiter(times=settings.RATE_LIMIT_AUTH_PER_MINUTE, seconds=60)
api_rate_limit = RateLimiter(times=settings.RATE_LIMIT_API_PER_MINUTE, seconds=60)
