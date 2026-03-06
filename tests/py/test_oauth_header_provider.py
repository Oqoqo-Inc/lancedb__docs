# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The LanceDB Authors

import time
from typing import Dict, Any

import lancedb
from lancedb.remote.header import OAuthProvider


def _fetch_oauth_token() -> Dict[str, Any]:
    """Example OAuth token fetcher.

    In a real application, this would call your identity provider (IdP)
    or OAuth authorization server to obtain an access token.
    """

    # This snippet is intentionally minimal and does not perform
    # any real network I/O. Replace with your own logic when
    # integrating with an OAuth server.
    return {"access_token": "example-token", "expires_in": 3600}


def test_oauth_header_provider_connect_cloud() -> None:
    # --8<-- [start:connect_cloud_oauth]
    from lancedb.remote.header import OAuthProvider

    # Define a token fetcher that talks to your OAuth/IdP system
    def fetch_token() -> Dict[str, Any]:
        # Call your OAuth server here and return the JSON payload
        # with at least an "access_token" field and optional
        # "expires_in" describing how long the token is valid.
        return {"access_token": "example-token", "expires_in": 3600}

    # Create an OAuthProvider that automatically refreshes the token
    # 5 minutes before it expires (default refresh_buffer_seconds=300).
    provider = OAuthProvider(token_fetcher=fetch_token)

    # Connect to LanceDB Cloud using OAuth-based bearer authentication.
    uri = "db://your-database-uri"
    api_key = "your-api-key"
    region = "us-east-1"

    db = lancedb.connect(
        uri,
        api_key=api_key,
        region=region,
        header_provider=provider,
    )
    # --8<-- [end:connect_cloud_oauth]

    # Basic smoke check to ensure the provider is wired up.
    assert db is not None


def test_oauth_header_provider_refresh() -> None:
    """Demonstrate automatic token refresh behavior."""

    calls = {"count": 0}

    def fetch_token() -> Dict[str, Any]:
        calls["count"] += 1
        return {"access_token": f"token-{calls['count']}", "expires_in": 1}

    provider = OAuthProvider(token_fetcher=fetch_token, refresh_buffer_seconds=0)

    # First call should fetch the initial token
    headers1 = provider.get_headers()
    assert headers1["Authorization"] == "Bearer token-1"

    # Wait for the token to expire and verify that a new token is fetched
    time.sleep(1.1)
    headers2 = provider.get_headers()
    assert headers2["Authorization"] == "Bearer token-2"
    assert calls["count"] == 2
