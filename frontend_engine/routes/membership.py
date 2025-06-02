"""
Membership Initiation System (MIS) Integration Endpoints
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Optional
import httpx
import os
import asyncio
from functools import lru_cache
from api.security import get_current_user

router = APIRouter(prefix="/api/frontend/membership", tags=["membership"])

MIS_BACKEND_URL = os.getenv("MIS_BACKEND_URL", "http://localhost:3000")

# Simple in-memory cache for invitation validation (expires after 5 min)
_invitation_cache = {}
_INVITATION_CACHE_TTL = 300  # seconds

def _cache_set(key, value):
    _invitation_cache[key] = (value, asyncio.get_event_loop().time())

def _cache_get(key):
    val = _invitation_cache.get(key)
    if val:
        value, ts = val
        if asyncio.get_event_loop().time() - ts < _INVITATION_CACHE_TTL:
            return value
        else:
            _invitation_cache.pop(key, None)
    return None

async def _httpx_post_with_retry(url, json, retries=2, timeout=5):
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=json)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            if attempt == retries:
                raise HTTPException(status_code=502, detail=f"MIS backend error: {str(e)}")
            await asyncio.sleep(0.5 * (attempt + 1))

@router.post("/validate-invitation")
async def validate_invitation(
    code: str = Body(...),
    pin: str = Body(...),
    user=Depends(get_current_user)
):
    """Validate invitation code and pin (proxy to MIS, with caching)"""
    cache_key = f"{code}:{pin}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    result = await _httpx_post_with_retry(f"{MIS_BACKEND_URL}/validate-invitation", {"code": code, "pin": pin})
    _cache_set(cache_key, result)
    return result

@router.post("/issue-key")
async def issue_membership_key(
    invitation_code: str = Body(...),
    user=Depends(get_current_user)
):
    """Issue membership key for a validated invitation (proxy to MIS, admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can issue membership keys.")
    return await _httpx_post_with_retry(f"{MIS_BACKEND_URL}/admin/approve-membership", {"invitation_code": invitation_code})

@router.post("/validate-key")
async def validate_membership_key(
    key: str = Body(...),
    user=Depends(get_current_user)
):
    """Validate a membership key (proxy to MIS)"""
    return await _httpx_post_with_retry(f"{MIS_BACKEND_URL}/validate-key", {"key": key})
