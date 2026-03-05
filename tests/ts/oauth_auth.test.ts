// snippet-start: TsOAuthAuth
import { connect, OAuthHeaderProvider } from "@lancedb/lancedb";

async function fetchToken() {
  // In production, replace this placeholder with a real call to your IdP
  // or internal auth service. The function should return an object with an
  // accessToken string and, optionally, an expiresIn field in seconds.
  const accessToken = process.env.LANCEDB_OAUTH_ACCESS_TOKEN ?? "dummy-token";
  return { accessToken, expiresIn: 3600 };
}

export async function connectWithOAuthHeaderProvider() {
  const dbUri = process.env.LANCEDB_URI ?? "db://your-database-uri";
  const region = process.env.LANCEDB_REGION ?? "us-east-1";

  const headerProvider = new OAuthHeaderProvider(fetchToken, {
    refreshBufferSeconds: 300,
  });

  const db = await connect(dbUri, {
    region,
    headerProvider,
  });

  // Exercise the connection in tests so this snippet stays valid.
  return db;
}

// snippet-end: TsOAuthAuth
