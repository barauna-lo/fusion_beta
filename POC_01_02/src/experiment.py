from __future__ import annotations

import platform
from importlib.metadata import version
from typing import Mapping

import colorednoise as cn
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

def generate_turbulence_series(n_points: int = 2042, seed: int = 42) -> pd.DataFrame:
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
    packages = [
        "colorednoise",
        "numpy",
        "pandas",
        "plotly",
        "snowflake-snowpark-python",
    ]
    package_versions = {}
    for package in packages:
        try:
            package_versions[package] = version(package)
        except Exception as exc:
            package_versions[package] = f"not_available: {exc}"

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": package_versions,
    }

def create_interactive_dashboard_html(data: pd.DataFrame) -> str:
    titles = [f"Power-law noise — beta = {BETAS[column]:g}" for column in BETAS]
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
    return fig.to_html(include_plotlyjs="cdn", full_html=True)

def build_experiment_outputs(run_id: str, n_points: int = 2042, seed: int = 42) -> dict:
    data = generate_turbulence_series(n_points=n_points, seed=seed)
    metadata = get_environment_metadata()
    metadata.update({
        "run_id": run_id,
        "n_points": n_points,
        "seed": seed,
        "betas": dict(BETAS),
    })
    return {
        "run_id": run_id,
        "series": data,
        "metadata": metadata,
        "dashboard_html": create_interactive_dashboard_html(data),
    }
