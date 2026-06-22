# POC 01 — Google Drive artifact storage

This version saves all experiment outputs inside an `output` folder created
under a user-provided path.

## Google Colab

```python
from google.colab import drive
drive.mount("/content/drive")
```

Then run:

```python
from experiment import run_experiment

artifacts = run_experiment(
    output_path="/content/drive/MyDrive/fusion_beta/POC_01",
    storage_backend="google_drive",
    n_points=2042,
    seed=42,
)
```

The files will be written to:

```text
/content/drive/MyDrive/fusion_beta/POC_01/output/
```

## Outputs

- `turbulence_series.parquet`
- `environment.json`
- `manifest.json`
- Four PNG charts
- `turbulence_dashboard.html`, with four rows and one column

## Local test

```python
artifacts = run_experiment(
    output_path=".",
    storage_backend="local",
)
```

This creates `./output`.
