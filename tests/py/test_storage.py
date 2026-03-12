# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The LanceDB Authors

import lancedb
import pytest

from lancedb import StorageOptionsProvider


class DummyTable:
    def __init__(self, name: str, storage_options: dict | None = None):
        self.name = name
        self.storage_options = storage_options


class DummyConnection:
    def __init__(self, uri: str, options: dict):
        self.uri = uri
        self.options = options
        self.created_tables: list[DummyTable] = []

    def create_table(self, name: str, data, storage_options: dict | None = None):
        table = DummyTable(name, storage_options=storage_options)
        self.created_tables.append(table)
        return table


@pytest.fixture
def fake_connect(monkeypatch):
    calls: list[DummyConnection] = []

    def _fake_connect(uri: str, **kwargs):
        conn = DummyConnection(uri, kwargs)
        calls.append(conn)
        return conn

    monkeypatch.setattr(lancedb, "connect", _fake_connect)
    return calls


def test_storage_snippets(fake_connect):
    # --8<-- [start:storage_connect_s3]
    db = lancedb.connect("s3://bucket/path")
    # --8<-- [end:storage_connect_s3]

    # --8<-- [start:storage_connect_gcs]
    db = lancedb.connect("gs://bucket/path")
    # --8<-- [end:storage_connect_gcs]

    # --8<-- [start:storage_connect_azure]
    db = lancedb.connect("az://bucket/path")
    # --8<-- [end:storage_connect_azure]

    # --8<-- [start:storage_connect_timeout]
    db = lancedb.connect(
        "s3://bucket/path",
        storage_options={"timeout": "60s"},
    )
    # --8<-- [end:storage_connect_timeout]

    # --8<-- [start:storage_table_timeout]
    table = db.create_table(
        "table",
        [{"a": 1, "b": 2}],
        storage_options={"timeout": "60s"},
    )
    # --8<-- [end:storage_table_timeout]

    # --8<-- [start:storage_s3_ddb]
    db = lancedb.connect(
        "s3+ddb://bucket/path?ddbTableName=my-dynamodb-table",
    )
    # --8<-- [end:storage_s3_ddb]

    # --8<-- [start:storage_s3_minio]
    db = lancedb.connect(
        "s3://bucket/path",
        storage_options={
            "region": "us-east-1",
            "endpoint": "http://minio:9000",
        },
    )
    # --8<-- [end:storage_s3_minio]

    # --8<-- [start:storage_s3_express]
    db = lancedb.connect(
        "s3://my-bucket--use1-az4--x-s3/path",
        storage_options={
            "region": "us-east-1",
            "s3_express": "true",
        },
    )
    # --8<-- [end:storage_s3_express]

    # --8<-- [start:storage_gcs_service_account]
    db = lancedb.connect(
        "gs://my-bucket/my-database",
        storage_options={
            "service_account": "path/to/service-account.json",
        },
    )
    # --8<-- [end:storage_gcs_service_account]

    # --8<-- [start:storage_azure_account]
    db = lancedb.connect(
        "az://my-container/my-database",
        storage_options={
            "account_name": "some-account",
            "account_key": "some-key",
        },
    )
    # --8<-- [end:storage_azure_account]

    # --8<-- [start:storage_tigris_connect]
    db = lancedb.connect(
        "s3://your-bucket/path",
        storage_options={
            "endpoint": "https://t3.storage.dev",
            "region": "auto",
        },
    )
    # --8<-- [end:storage_tigris_connect]

    # --8<-- [start:storage_options_provider_temporary_creds]
    class TemporaryCredentialProvider(StorageOptionsProvider):
        """Example provider for short-lived cloud credentials.

        In a real application, this class would call your IAM system or
        cloud SDK (for example AWS STS, GCP STS, or Azure Managed Identity)
        to fetch temporary credentials and their expiration time.
        """

        def __init__(self, role_arn: str, session_name: str):
            self.role_arn = role_arn
            self.session_name = session_name

        def fetch_storage_options(self) -> dict[str, str]:
            """Return storage options for the current session.

            The optional "expires_at_millis" key tells LanceDB when these
            options expire so it can refresh them automatically.
            See `StorageOptionsProvider.fetch_storage_options` in
            `lancedb/io.py` for details.
            """

            # In production code, replace this with a call to your
            # cloud provider's SDK to assume a role or fetch a token.
            # For example, with AWS STS you would return the access key,
            # secret key, session token, and expiration time.
            return {
                "aws_access_key_id": "ACCESS_KEY_ID",
                "aws_secret_access_key": "SECRET_ACCESS_KEY",
                "aws_session_token": "SESSION_TOKEN",
                # Unix timestamp in milliseconds for when the credentials expire.
                "expires_at_millis": "1735689600000",
            }

        def provider_id(self) -> str:
            """Stable identifier so LanceDB can cache connections.

            Providers with the same `provider_id` share the same underlying
            object store client. Include fields that uniquely identify the
            source of credentials but avoid secrets.
            """

            return f"temporary-aws-role:{self.role_arn}:{self.session_name}"

    db = lancedb.connect("s3://bucket/path")

    # Use the provider when creating a table so LanceDB can refresh
    # credentials transparently when they expire.
    table = db.create_table(
        "events",
        [{"a": 1, "b": 2}],
        storage_options_provider=TemporaryCredentialProvider(
            role_arn="arn:aws:iam::123456789012:role/ExampleRole",
            session_name="example-session",
        ),
    )

    # You can also provide the same provider when opening a table.
    table = db.open_table(
        "events",
        storage_options_provider=TemporaryCredentialProvider(
            role_arn="arn:aws:iam::123456789012:role/ExampleRole",
            session_name="example-session",
        ),
    )
    # --8<-- [end:storage_options_provider_temporary_creds]

    assert len(fake_connect) == 10
    assert all(
        conn.uri.startswith(("s3://", "gs://", "az://", "s3+ddb://"))
        for conn in fake_connect
    )
