// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: Copyright The LanceDB Authors
+
+// Docs snippets for OAuth/Bearer authentication in TypeScript.
+//
+// These examples are used to generate documentation snippets showing how to
+// configure LanceDB's TypeScript SDK with OAuth-style Bearer token
+// authentication using header providers.
+
+import {
+  OAuthHeaderProvider,
+  StaticHeaderProvider,
+  type TokenResponse,
+  connect,
+} from "@lancedb/lancedb";
+
+// --8<-- [start:auth_oauth_ts_provider]
+async function fetchToken(): Promise<TokenResponse> {
+  // Call your OAuth or IDP service here instead of returning a
+  // hard-coded token.
+  const response = await fetch("https://oauth.example.com/token", {
+    method: "POST",
+    headers: { "Content-Type": "application/json" },
+    body: JSON.stringify({
+      grant_type: "client_credentials",
+      client_id: process.env.CLIENT_ID,
+      client_secret: process.env.CLIENT_SECRET,
+    }),
+  });
+
+  const data = await response.json();
+  return {
+    accessToken: data.access_token,
+    expiresIn: data.expires_in, // seconds until expiry
+  };
+}
+
+const oauthProvider = new OAuthHeaderProvider(fetchToken, 5 * 60); // 5 minute buffer
+// --8<-- [end:auth_oauth_ts_provider]
+
+// --8<-- [start:auth_oauth_ts_connect]
+const db = await connect(
+  "db://your-database-uri",
+  {
+    apiKey: process.env.LANCEDB_API_KEY!, // still required for Cloud/Enterprise
+    region: process.env.LANCEDB_REGION ?? "us-east-1",
+  },
+  undefined, // optional Session
+  oauthProvider,
+);
+// --8<-- [end:auth_oauth_ts_connect]
+
+// --8<-- [start:auth_oauth_ts_function_provider]
+// Alternatively, you can pass a function that returns headers directly.
+const dbWithFunctionProvider = await connect(
+  "db://your-database-uri",
+  {
+    apiKey: process.env.LANCEDB_API_KEY!,
+    region: process.env.LANCEDB_REGION ?? "us-east-1",
+  },
+  undefined,
+  async () => {
+    const token = await fetchToken();
+    return {
+      Authorization: `Bearer ${token.accessToken}`,
+    };
+  },
+);
+// --8<-- [end:auth_oauth_ts_function_provider]
+
+// --8<-- [start:auth_oauth_ts_static_header]
+// For simple API key or static Bearer tokens, you can also use StaticHeaderProvider.
+const staticProvider = new StaticHeaderProvider({
+  Authorization: "Bearer example-static-token",
+  "X-Request-Source": "docs-example",
+});
+
+const dbWithStaticProvider = await connect(
+  "db://your-database-uri",
+  {
+    apiKey: process.env.LANCEDB_API_KEY!,
+    region: process.env.LANCEDB_REGION ?? "us-east-1",
+  },
+  undefined,
+  staticProvider,
+);
+// --8<-- [end:auth_oauth_ts_static_header]
+
+void db;
+void dbWithFunctionProvider;
+void dbWithStaticProvider;
