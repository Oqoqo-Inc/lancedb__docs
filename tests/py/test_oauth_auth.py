# snippet-start: PyOAuthAuth
from typing import Dict, Any
import os

import lancedb
from lancedb.remote.header import OAuthProvider


def token_fetcher() -> Dict[str, Any]:
    """Fetch an OAuth access token from an IdP or internal auth service.

    In production, replace this placeholder with a real call to your identity
    provider or token broker. The function must return a mapping with an
    "access_token" key and, optionally, an "expires_in" field indicating
    token lifetime in seconds.
    """

    # This placeholder mirrors the structure expected by OAuthProvider.
    # Use an environment variable in tests so the snippet remains valid.
    access_token = os.environ.get("LANCEDB_OAUTH_ACCESS_TOKEN", "dummy-token")
    return {"access_token": access_token, "expires_in": 3600}


def connect_with_oauth_header_provider() -> None:
    """Example connection using OAuthProvider for Authorization headers.

    This example shows how to configure a LanceDB Cloud/Enterprise connection
    that uses short-lived OAuth/Bearer tokens instead of long-lived API keys.
    The OAuthProvider caches tokens and refreshes them automatically before
    they expire.
    """

    uri = "db://your-database-uri"
    region = "us-east-1"

    oauth_provider = OAuthProvider(token_fetcher, refresh_buffer_seconds=300)

    # When connecting, pass the header provider so that the client adds
    # Authorization: Bearer <token> to each outgoing request.
    db = lancedb.connect(uri=uri, region=region, header_provider=oauth_provider)

    # Exercise the connection in tests so this snippet stays valid.
    _ = db  # pragma: no cover


# snippet-end: PyOAuthAuth
