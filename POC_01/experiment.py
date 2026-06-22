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


def generate_turbulence_series(n_points: int = 2042, seed: int = 42) -> pd.DataFrame:
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
    """Return the main environment and package versions."""
    packages = [
        "colorednoise",
        "numpy",
        "pandas",
        "pyarrow",
        "matplotlib",
        "plotly",
    ]
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {package: version(package) for package in packages},
    }


def create_static_charts(data: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Create one PNG chart for each generated series."""
    chart_paths: list[Path] = []

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


def create_interactive_chart(data: pd.DataFrame, output_path: Path) -> Path:
    """Create one interactive Plotly HTML with all four series."""
    fig = go.Figure()

    for column, color in COLORS.items():
        beta = BETAS[column]
        fig.add_trace(
            go.Scatter(
                x=data["step"],
                y=data[column],
                mode="lines",
                name=f"beta = {beta:g}",
                line={"color": color, "width": 1.2},
            )
        )

    fig.update_layout(
        title="Power-law turbulence series",
        xaxis_title="Step",
        yaxis_title="Value",
        template="plotly_white",
        hovermode="x unified",
    )
    fig.write_html(output_path, include_plotlyjs="cdn")
    return output_path


def save_artifacts(
    data: pd.DataFrame,
    output_uri: str | Path = "outputs",
    storage_backend: str = "local",
) -> dict[str, str]:
    """Save all artifacts produced by the experiment."""
    if storage_backend != "local":
        raise NotImplementedError(
            "Only the local backend is available in POC 01. "
            "A GCS backend will be added later."
        )

    output_dir = Path(output_uri)
    output_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = output_dir / "turbulence_series.parquet"
    metadata_path = output_dir / "environment.json"
    html_path = output_dir / "turbulence_series.html"

    data.to_parquet(parquet_path, index=False)
    metadata_path.write_text(
        json.dumps(get_environment_metadata(), indent=2),
        encoding="utf-8",
    )

    static_paths = create_static_charts(data, output_dir)
    create_interactive_chart(data, html_path)

    artifacts = {
        "parquet": str(parquet_path),
        "environment": str(metadata_path),
        "interactive_chart": str(html_path),
        **{f"chart_{path.stem}": str(path) for path in static_paths},
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(artifacts, indent=2),
        encoding="utf-8",
    )
    artifacts["manifest"] = str(manifest_path)
    return artifacts


def run_experiment(
    n_points: int = 2042,
    seed: int = 42,
    output_uri: str | Path = "outputs",
    storage_backend: str = "local",
) -> dict[str, str]:
    """Run the complete POC 01 experiment."""
    data = generate_turbulence_series(n_points=n_points, seed=seed)
    return save_artifacts(
        data=data,
        output_uri=output_uri,
        storage_backend=storage_backend,
    )


if __name__ == "__main__":
    print(json.dumps(run_experiment(), indent=2))
