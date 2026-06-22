# POC 01 — Local/Colab artifact generation

Minimal experiment for validating deterministic artifact generation before the Hex → GCP → GCS integration.

## Outputs

- `turbulence_series.parquet`
- `environment.json`
- Four static PNG charts
- One interactive Plotly HTML
- `manifest.json`

## Run

```bash
pip install -r requirements.txt
python experiment.py
```

Or open `poc_01_colab.ipynb` in Google Colab.

The main interface is:

```python
run_experiment(
    n_points=2042,
    seed=42,
    output_uri="outputs",
    storage_backend="local",
)
```

`save_artifacts` is used as the standard persistence function name. In this POC, only the local backend is implemented. A GCS backend can later be added without changing the experiment interface.
