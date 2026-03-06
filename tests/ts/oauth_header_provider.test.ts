// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: Copyright The LanceDB Authors

import { expect, test } from "@jest/globals";
import * as lancedb from "@lancedb/lancedb";

const ONE_SECOND = 1000;

// --8<-- [start:connect_cloud_oauth]
import { OAuthHeaderProvider, TokenResponse } from "@lancedb/lancedb";

async function fetchToken(): Promise<TokenResponse> {
  // In a real application, call your OAuth/IDP server here and
  // return an object with `accessToken` and optional `expiresIn`.
  return {
    accessToken: "example-token",
    expiresIn: 3600,
  };
}

// Create an OAuthHeaderProvider that automatically refreshes the token
// 5 minutes before it expires (default refreshBufferSeconds=300).
const provider = new OAuthHeaderProvider(fetchToken);

async function connectWithOAuth(uri: string) {
  const db = await lancedb.connect(
    uri,
    {
      apiKey: "your-api-key",
      hostOverride: "https://your-region.api.lancedb.com",
    },
    undefined, // session
    provider, // headerProvider
  );
  return db;
}
// --8<-- [end:connect_cloud_oauth]


test("oauth header provider refreshes tokens", async () => {
  let callCount = 0;

  const tokenFetcher = async () => {
    callCount++;
    return {
      accessToken: `token-${callCount}`,
      expiresIn: 1,
    } satisfies TokenResponse;
  };

  const oauthProvider = new OAuthHeaderProvider(tokenFetcher, 0);
  await oauthProvider.refreshToken();

  const headers1 = oauthProvider.getHeaders();
  expect(headers1.authorization).toBe("Bearer token-1");

  // Wait for token to expire and verify that a new token is fetched
  await new Promise((resolve) => setTimeout(resolve, ONE_SECOND + 100));

  await oauthProvider.refreshToken();
  const headers2 = oauthProvider.getHeaders();
  expect(headers2.authorization).toBe("Bearer token-2");
  expect(callCount).toBe(2);
});
