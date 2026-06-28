# Example Hex cell.
# This assumes Hex already has a Snowflake connection configured.

run_id = "poc_01_02_from_hex_001"

query = f"""
CALL FUSION_POC_DB.POC_01_02.POC_01_02_RUN_EXPERIMENT(
    '{run_id}',
    2042,
    42
)
"""

# result = snowflake_connection.query(query)
# display(result)

series_query = f"""
SELECT *
FROM FUSION_POC_DB.POC_01_02.POC_01_02_TURBULENCE_SERIES
WHERE RUN_ID = '{run_id}'
ORDER BY STEP
"""

manifest_query = f"""
SELECT *
FROM FUSION_POC_DB.POC_01_02.POC_01_02_ARTIFACT_MANIFEST
WHERE RUN_ID = '{run_id}'
ORDER BY CREATED_AT
"""
