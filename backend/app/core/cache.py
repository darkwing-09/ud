"""Redis cache client, decorator, and helpers."""
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from typing import Any

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Client Instances ──────────────────────────────────────────
_cache_client: aioredis.Redis | None = None
_queue_client: aioredis.Redis | None = None


async def get_cache_client() -> aioredis.Redis:
    global _cache_client
    if _cache_client is None:
        _cache_client = aioredis.from_url(
            settings.redis_cache_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _cache_client


async def get_queue_client() -> aioredis.Redis:
    global _queue_client
    if _queue_client is None:
        _queue_client = aioredis.from_url(
            settings.CELERY_BROKER_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _queue_client


async def ping_redis() -> bool:
    """Health check for Redis."""
    client = await get_cache_client()
    return await client.ping()


# ── Cache Operations ──────────────────────────────────────────
async def cache_get(key: str) -> Any | None:
    client = await get_cache_client()
    value = await client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = await get_cache_client()
    await client.setex(key, ttl_seconds, json.dumps(value, default=str))


async def cache_delete(key: str) -> None:
    client = await get_cache_client()
    await client.delete(key)


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern. Returns count deleted."""
    client = await get_cache_client()
    keys = await client.keys(pattern)
    if not keys:
        return 0
    return await client.delete(*keys)


# ── Token Blacklist ───────────────────────────────────────────
TOKEN_BLACKLIST_PREFIX = "blacklist:token:"
REFRESH_FAMILY_PREFIX = "refresh:family:"


async def blacklist_token(jti: str, expires_in_seconds: int) -> None:
    client = await get_cache_client()
    await client.setex(f"{TOKEN_BLACKLIST_PREFIX}{jti}", expires_in_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    client = await get_cache_client()
    return await client.exists(f"{TOKEN_BLACKLIST_PREFIX}{jti}") == 1


async def blacklist_refresh_family(family_id: str, expires_in_seconds: int) -> None:
    """Blacklist entire token family (theft detected)."""
    client = await get_cache_client()
    await client.setex(f"{REFRESH_FAMILY_PREFIX}{family_id}", expires_in_seconds, "1")


async def is_family_blacklisted(family_id: str) -> bool:
    client = await get_cache_client()
    return await client.exists(f"{REFRESH_FAMILY_PREFIX}{family_id}") == 1


# ── Named Cache Keys ──────────────────────────────────────────
def timetable_cache_key(school_id: str, section_id: str) -> str:
    return f"timetable:{school_id}:{section_id}"


def analytics_cache_key(school_id: str, report_type: str) -> str:
    return f"analytics:{school_id}:{report_type}"


def fee_summary_cache_key(school_id: str, student_id: str) -> str:
    return f"fee_summary:{school_id}:{student_id}"


# ── TTL Constants ─────────────────────────────────────────────
class CacheTTL:
    TIMETABLE = 3600          # 1 hour — changes rarely
    ANALYTICS = 900           # 15 min — heavy compute
    FEE_SUMMARY = 300         # 5 min — updates on payment
    ATTENDANCE_REPORT = 600   # 10 min
    TOKEN_BLACKLIST = 86400   # 24 hours
    RATE_LIMIT = 60           # 1 minute windows


async def close_cache() -> None:
    global _cache_client, _queue_client
    if _cache_client:
        await _cache_client.aclose()
        _cache_client = None
    if _queue_client:
        await _queue_client.aclose()
        _queue_client = None
