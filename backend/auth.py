"""
JWT Authentication module using JWKS (asymmetric key verification).

Better Auth exposes public keys at /api/auth/jwks. This module fetches
those keys and uses them to verify JWT tokens from incoming requests.
"""

import os
import logging
from typing import Any

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Environment validation at import time
BETTER_AUTH_URL = os.environ.get("BETTER_AUTH_URL")
if not BETTER_AUTH_URL:
    raise RuntimeError("BETTER_AUTH_URL environment variable is not set")

# JWKS cache
_jwks_cache: dict[str, Any] = {}
_cached_keys: dict[str, Any] = {}

security = HTTPBearer(auto_error=False)


async def fetch_jwks() -> dict[str, Any]:
    """Fetch JWKS from Better Auth endpoint."""
    global _jwks_cache

    # Use cached JWKS if available
    if _jwks_cache:
        print(f"[AUTH DEBUG] Using cached JWKS")
        return _jwks_cache

    # Re-read BETTER_AUTH_URL in case it changed
    auth_url = os.environ.get("BETTER_AUTH_URL", BETTER_AUTH_URL)
    jwks_url = f"{auth_url}/api/auth/jwks"
    print(f"[AUTH DEBUG] Fetching JWKS from: {jwks_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            print(f"[AUTH DEBUG] JWKS response status: {response.status_code}")
            response.raise_for_status()
            _jwks_cache = response.json()
            print(f"[AUTH DEBUG] JWKS fetched successfully, keys: {len(_jwks_cache.get('keys', []))}")
            return _jwks_cache
    except httpx.HTTPError as e:
        print(f"[AUTH DEBUG] JWKS fetch failed: {e}")
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to verify authentication",
        ) from e


def get_public_key_from_jwks(jwks: dict[str, Any], kid: str | None = None) -> Any:
    """Extract public key from JWKS."""
    global _cached_keys
    from jwt import PyJWK

    keys = jwks.get("keys", [])
    if not keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No keys available for verification",
        )

    # If kid specified, find matching key
    if kid:
        for key in keys:
            if key.get("kid") == kid:
                cache_key = kid
                if cache_key not in _cached_keys:
                    jwk = PyJWK.from_dict(key)
                    _cached_keys[cache_key] = jwk.key
                return _cached_keys[cache_key]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Key not found",
        )

    # Otherwise use first key
    key = keys[0]
    cache_key = key.get("kid", "default")
    if cache_key not in _cached_keys:
        jwk = PyJWK.from_dict(key)
        _cached_keys[cache_key] = jwk.key

    return _cached_keys[cache_key]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """
    FastAPI dependency that extracts and verifies the JWT token.

    Returns a dict with user_id and email from the token payload.
    Raises HTTPException 401 for missing, invalid, or expired tokens.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    print(f"[AUTH DEBUG] Verifying token: {token[:50]}...")

    try:
        # Get unverified header to find kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        print(f"[AUTH DEBUG] Token kid: {kid}")

        # Fetch JWKS and get public key
        jwks = await fetch_jwks()
        public_key = get_public_key_from_jwks(jwks, kid)

        # Verify and decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["EdDSA", "RS256"],
            options={"verify_aud": False},
        )

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return {"user_id": user_id, "email": email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
