# POC_01_02 — Snowflake Runtime Validation

This POC validates the new flow:

```text
HEX → Snowflake → GitHub repository clone → Python execution in Snowflake → Snowflake output tables
```

The goal is to prove that Snowflake can execute a simple Python application versioned in GitHub and persist generated outputs back into Snowflake tables.

## Execution order

```text
sql/00_setup_environment.sql
sql/01_git_integration.sql
sql/02_create_objects.sql
sql/03_run_poc.sql
```

## Output tables

- `POC_01_02_TURBULENCE_SERIES`
- `POC_01_02_ENVIRONMENT`
- `POC_01_02_ARTIFACT_MANIFEST`
