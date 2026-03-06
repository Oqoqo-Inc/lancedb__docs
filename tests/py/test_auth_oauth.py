# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The LanceDB Authors
+
+"""Docs snippets for OAuth/Bearer authentication in Python.
+
+These examples are used to generate documentation snippets demonstrating how to
+configure OAuth-style Bearer token authentication for LanceDB Cloud/Enterprise
+using the Python SDK's header provider framework.
+"""
+
+from __future__ import annotations
+
+from typing import Dict
+
+import lancedb
+from lancedb.remote.header import OAuthProvider
+
+
+def _make_oauth_provider() -> OAuthProvider:
+    """Create an OAuthProvider that fetches and refreshes access tokens.
+
+    This helper is intentionally simple for documentation purposes. In a real
+    application you would call your IdP / OAuth server instead of returning a
+    hard-coded token.
+    """
+
+    def fetch_token() -> Dict[str, object]:
+        # Replace this with a real client that talks to your IdP.
+        # The function must return at least an ``access_token`` field and can
+        # optionally include ``expires_in`` (in seconds) so LanceDB can
+        # proactively refresh the token before it expires.
+        return {
+            "access_token": "example-oauth-access-token",
+            "expires_in": 3600,
+        }
+
+    return OAuthProvider(fetch_token, refresh_buffer_seconds=300)
+
+
+def _connect_with_oauth() -> None:
+    """Connect to LanceDB Cloud/Enterprise with OAuth/Bearer auth.
+
+    The header provider automatically refreshes the token when it is close to
+    expiring. All requests will include an ``Authorization: Bearer`` header in
+    addition to the required ``x-api-key``.
+    """
+
+    # --8<-- [start:auth_oauth_python_connect]
+    from lancedb.remote.header import OAuthProvider
+
+    def fetch_token() -> Dict[str, object]:
+        # Call your OAuth or IDP service here instead of returning a
+        # hard-coded token.
+        return {
+            "access_token": "example-oauth-access-token",
+            "expires_in": 3600,  # seconds until expiry
+        }
+
+    provider = OAuthProvider(fetch_token, refresh_buffer_seconds=300)
+
+    db = lancedb.connect(
+        uri="db://your-database-uri",
+        api_key="your-api-key",  # still required for LanceDB Cloud/Enterprise
+        region="us-east-1",
+        header_provider=provider,
+    )
+    # --8<-- [end:auth_oauth_python_connect]
+
+    # Use ``db`` as usual, e.g. ``db.table_names()``
+
+
+def _connect_with_oauth_no_expiry() -> None:
+    """Example using a token that does not report an expiry.
+
+    In this case LanceDB will reuse the same token until your fetcher changes
+    it (for example after a rotation), but will not schedule automatic
+    refreshes based on ``expires_in``.
+    """
+
+    # --8<-- [start:auth_oauth_python_no_expiry]
+    from lancedb.remote.header import OAuthProvider
+
+    def fetch_token() -> Dict[str, object]:
+        # Token without ``expires_in``; LanceDB will treat it as non-expiring.
+        return {
+            "access_token": "example-non-expiring-token",
+        }
+
+    provider = OAuthProvider(fetch_token)
+
+    db = lancedb.connect(
+        uri="db://your-database-uri",
+        api_key="your-api-key",
+        region="us-east-1",
+        header_provider=provider,
+    )
+    # --8<-- [end:auth_oauth_python_no_expiry]
+
+    _ = db
