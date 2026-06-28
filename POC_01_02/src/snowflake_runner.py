from __future__ import annotations

import json
from uuid import uuid4

from snowflake.snowpark import Session

from experiment import build_experiment_outputs
from savefile import save_artifacts

def main(session: Session, run_id: str | None = None, n_points: int = 2042, seed: int = 42) -> str:
    final_run_id = run_id or f"poc_01_02_{uuid4().hex[:12]}"
    outputs = build_experiment_outputs(
        run_id=final_run_id,
        n_points=n_points,
        seed=seed,
    )
    save_result = save_artifacts(
        session=session,
        outputs=outputs,
        storage_backend="snowflake",
    )
    return json.dumps(save_result)
