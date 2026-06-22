from __future__ import annotations

import json
import platform
from importlib.metadata import version
from pathlib import Path
from typing import Mapping

import colorednoise as cn
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


BETAS: Mapping[str, float] = {
    "beta_0": 0.0,
    "beta_1": 1.0,
    "beta_5_3": 5 / 3,
    "beta_2": 2.0,
}

COLORS: Mapping[str, str] = {
    "beta_0": "black",
    "beta_1": "pink",
    "beta_5_3": "blue",
    "beta_2": "red",
}


def generate_turbulence_series(
    n_points: int = 2042,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate reproducible power-law noise time series."""
    if n_points <= 0:
        raise ValueError("n_points must be greater than zero.")

    data = {"step": range(n_points)}

    for index, (name, beta) in enumerate(BETAS.items()):
        data[name] = cn.powerlaw_psd_gaussian(
            exponent=beta,
            size=n_points,
            random_state=seed + index,
        )

    return pd.DataFrame(data)


def get_environment_metadata() -> dict:
    """Return Python, platform, and package versions."""
    packages = (
        "colorednoise",
        "numpy",
        "pandas",
        "pyarrow",
        "matplotlib",
        "plotly",
    )

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {package: version(package) for package in packages},
    }


def resolve_output_directory(
    output_path: str | Path,
    storage_backend: str = "google_drive",
) -> Path:
    """
    Resolve and create the experiment output directory.

    For Google Drive in Colab, `output_path` must point to a mounted Drive
    directory, for example:
    `/content/drive/MyDrive/fusion_beta/POC_01`.

    An `output` folder is always created inside the supplied path.
    """
    supported_backends = {"local", "google_drive"}

    if storage_backend not in supported_backends:
        raise ValueError(
            f"Unsupported storage_backend={storage_backend!r}. "
            f"Expected one of {sorted(supported_backends)}."
        )

    root = Path(output_path).expanduser()

    if storage_backend == "google_drive":
        drive_root = Path("/content/drive")
        if not drive_root.exists():
            raise RuntimeError(
                "Google Drive is not mounted. In Colab, run:\n"
                "from google.colab import drive\n"
                "drive.mount('/content/drive')"
            )

    output_dir = root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def create_static_charts(
    data: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    """Create one PNG chart for each generated series."""
    chart_paths = []

    for column, color in COLORS.items():
        beta = BETAS[column]
        path = output_dir / f"{column}.png"

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(data["step"], data[column], color=color, linewidth=1)
        ax.set(
            title=f"Power-law noise — beta = {beta:g}",
            xlabel="Step",
            ylabel="Value",
        )
        ax.grid(alpha=0.2)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)

        chart_paths.append(path)

    return chart_paths


def create_interactive_dashboard(
    data: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Create a Plotly dashboard with four rows and one column."""
    titles = [
        f"Power-law noise — beta = {BETAS[column]:g}"
        for column in BETAS
    ]

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=titles,
    )

    for row, (column, color) in enumerate(COLORS.items(), start=1):
        beta = BETAS[column]
        fig.add_trace(
            go.Scatter(
                x=data["step"],
                y=data[column],
                mode="lines",
                name=f"beta = {beta:g}",
                line={"color": color, "width": 1.2},
                showlegend=False,
            ),
            row=row,
            col=1,
        )
        fig.update_yaxes(title_text="Value", row=row, col=1)

    fig.update_xaxes(title_text="Step", row=4, col=1)
    fig.update_layout(
        title="Power-law Turbulence Dashboard",
        height=1200,
        template="plotly_white",
        hovermode="x",
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
    return output_path


def save_artifacts(
    data: pd.DataFrame,
    output_path: str | Path,
    storage_backend: str = "google_drive",
) -> dict[str, str]:
    """
    Persist all experiment outputs.

    `save_artifacts` is the standard persistence entry point. It supports
    local paths and mounted Google Drive paths.
    """
    output_dir = resolve_output_directory(
        output_path=output_path,
        storage_backend=storage_backend,
    )

    parquet_path = output_dir / "turbulence_series.parquet"
    metadata_path = output_dir / "environment.json"
    dashboard_path = output_dir / "turbulence_dashboard.html"

    data.to_parquet(parquet_path, index=False)

    metadata_path.write_text(
        json.dumps(get_environment_metadata(), indent=2),
        encoding="utf-8",
    )

    static_paths = create_static_charts(data, output_dir)
    create_interactive_dashboard(data, dashboard_path)

    artifacts = {
        "output_directory": str(output_dir),
        "parquet": str(parquet_path),
        "environment": str(metadata_path),
        "interactive_dashboard": str(dashboard_path),
        **{
            f"chart_{path.stem}": str(path)
            for path in static_paths
        },
    }

    manifest_path = output_dir / "manifest.json"
    artifacts["manifest"] = str(manifest_path)

    manifest_path.write_text(
        json.dumps(artifacts, indent=2),
        encoding="utf-8",
    )

    return artifacts


def run_experiment(
    output_path: str | Path,
    storage_backend: str = "google_drive",
    n_points: int = 2042,
    seed: int = 42,
) -> dict[str, str]:
    """Run the complete POC 01 experiment."""
    data = generate_turbulence_series(
        n_points=n_points,
        seed=seed,
    )

    return save_artifacts(
        data=data,
        output_path=output_path,
        storage_backend=storage_backend,
    )


if __name__ == "__main__":
    result = run_experiment(
        output_path=".",
        storage_backend="local",
    )
    print(json.dumps(result, indent=2))
