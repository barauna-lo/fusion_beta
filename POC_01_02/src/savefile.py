from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from snowflake.snowpark import Session

DEFAULT_TABLES = {
    "series": "POC_01_02_TURBULENCE_SERIES",
    "environment": "POC_01_02_ENVIRONMENT",
    "manifest": "POC_01_02_ARTIFACT_MANIFEST",
}

class SnowflakeArtifactSaver:
    def __init__(self, session: Session, table_names: dict[str, str] | None = None) -> None:
        self.session = session
        self.table_names = table_names or DEFAULT_TABLES

    def save_series(self, run_id: str, data: pd.DataFrame) -> str:
        table_name = self.table_names["series"]
        series_df = data.copy()
        series_df.insert(0, "RUN_ID", run_id)
        series_df.columns = [column.upper() for column in series_df.columns]
        self.session.write_pandas(
            series_df,
            table_name=table_name,
            auto_create_table=False,
            overwrite=False,
        )
        return table_name

    def save_environment(self, run_id: str, metadata: dict[str, Any]) -> str:
        table_name = self.table_names["environment"]
        metadata_json = json.dumps(metadata).replace("'", "''")
        self.session.sql(f"""
            INSERT INTO {table_name} (RUN_ID, METADATA_JSON, CREATED_AT)
            SELECT '{run_id}', PARSE_JSON('{metadata_json}'), CURRENT_TIMESTAMP()
        """).collect()
        return table_name

    def save_manifest(self, artifact_rows: list[dict[str, Any]]) -> str:
        table_name = self.table_names["manifest"]
        manifest_df = pd.DataFrame(artifact_rows)
        manifest_df.columns = [column.upper() for column in manifest_df.columns]
        self.session.write_pandas(
            manifest_df,
            table_name=table_name,
            auto_create_table=False,
            overwrite=False,
        )
        return table_name

    def save_html_dashboard(self, run_id: str, dashboard_html: str) -> str:
        table_name = self.table_names["manifest"]
        escaped_html = dashboard_html.replace("'", "''")
        self.session.sql(f"""
            INSERT INTO {table_name} (
                RUN_ID,
                ARTIFACT_NAME,
                ARTIFACT_TYPE,
                STORAGE_BACKEND,
                STORAGE_REFERENCE,
                CONTENT_TEXT,
                CREATED_AT
            )
            SELECT
                '{run_id}',
                'turbulence_dashboard.html',
                'html',
                'snowflake_table',
                '{table_name}',
                '{escaped_html}',
                CURRENT_TIMESTAMP()
        """).collect()
        return table_name

def save_artifacts(session: Session, outputs: dict[str, Any], storage_backend: str = "snowflake") -> dict[str, Any]:
    if storage_backend != "snowflake":
        raise ValueError("This POC only supports storage_backend='snowflake'.")

    run_id = outputs["run_id"]
    saver = SnowflakeArtifactSaver(session=session)

    series_table = saver.save_series(run_id=run_id, data=outputs["series"])
    environment_table = saver.save_environment(run_id=run_id, metadata=outputs["metadata"])

    manifest_table = saver.save_manifest([
        {
            "run_id": run_id,
            "artifact_name": "turbulence_series",
            "artifact_type": "snowflake_table",
            "storage_backend": "snowflake",
            "storage_reference": series_table,
            "content_text": None,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "run_id": run_id,
            "artifact_name": "environment_metadata",
            "artifact_type": "snowflake_variant",
            "storage_backend": "snowflake",
            "storage_reference": environment_table,
            "content_text": None,
            "created_at": datetime.now(timezone.utc),
        },
    ])

    saver.save_html_dashboard(run_id=run_id, dashboard_html=outputs["dashboard_html"])

    return {
        "run_id": run_id,
        "storage_backend": storage_backend,
        "series_table": series_table,
        "environment_table": environment_table,
        "manifest_table": manifest_table,
    }
