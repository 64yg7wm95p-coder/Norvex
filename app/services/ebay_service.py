import os
from datetime import UTC, datetime, timedelta

import requests
from fastapi import HTTPException

from ..database import get_db_connection


EBAY_IDENTITY_URL = "https://api.ebay.com/identity/v1/oauth2/token"


def exchange_code_for_token(user_id: int, code: str) -> str:
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    redirect_uri = os.getenv("EBAY_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(
            status_code=500,
            detail="eBay OAuth ayarları eksik.",
        )

    response = requests.post(
        EBAY_IDENTITY_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        auth=(client_id, client_secret),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        timeout=30,
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail=f"eBay OAuth callback başarısız: {response.text}",
        )

    data = response.json()

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expires_in = int(data.get("expires_in", 7200))

    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="eBay token cevabı eksik.",
        )

    expires_at = (
        datetime.now(UTC) + timedelta(seconds=expires_in)
    ).isoformat()

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE users
        SET
            ebay_refresh_token = ?,
            ebay_access_token = ?,
            ebay_token_expires_at = ?
        WHERE id = ?
        """,
        (
            refresh_token,
            access_token,
            expires_at,
            user_id,
        ),
    )
    conn.commit()
    conn.close()

    return access_token


def refresh_access_token(
    user_id: int,
    refresh_token: str,
) -> str:
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="eBay OAuth ayarları eksik.",
        )

    response = requests.post(
        EBAY_IDENTITY_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        auth=(client_id, client_secret),
        ,data={
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "scope": " ".join([
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    ]),
    },
        timeout=30,
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail=f"eBay access token yenileme başarısız: {response.text}",
        )

    data = response.json()

    access_token = data.get("access_token")
    expires_in = int(data.get("expires_in", 7200))

    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="eBay access token cevabı eksik.",
        )

    expires_at = (
        datetime.now(UTC) + timedelta(seconds=expires_in)
    ).isoformat()

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE users
        SET
            ebay_access_token = ?,
            ebay_token_expires_at = ?
        WHERE id = ?
        """,
        (
            access_token,
            expires_at,
            user_id,
        ),
    )
    conn.commit()
    conn.close()

    return access_token