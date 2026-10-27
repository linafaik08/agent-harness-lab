"""Per-version metrics computed from the table of trials."""

from __future__ import annotations

import pandas as pd


def summarize(trials: pd.DataFrame) -> pd.DataFrame:
    """Aggregates trial rows into one row per harness version.

    Args:
        trials: One row per trial with the columns "version", "task", "passed",
            "cost_usd" and "steps".

    Returns:
        A frame indexed by version with:
        - pass_at_1: the share of trials that passed, averaged over tasks, which
          estimates the chance that a single attempt succeeds;
        - pass_hat_k: the share of tasks where all k trials passed, a measure of
          reliability rather than capability;
        - cost_per_task and steps_per_task: means over every trial;
        - k: the number of trials per task.
    """
    per_task = trials.groupby(["version", "task"]).agg(
        successes=("passed", "sum"),
        k=("passed", "size"),
        cost=("cost_usd", "mean"),
        steps=("steps", "mean"),
    )
    per_task["rate"] = per_task["successes"] / per_task["k"]
    per_task["all_passed"] = per_task["successes"] == per_task["k"]
    summary = per_task.groupby("version").agg(
        pass_at_1=("rate", "mean"),
        pass_hat_k=("all_passed", "mean"),
        cost_per_task=("cost", "mean"),
        steps_per_task=("steps", "mean"),
        k=("k", "min"),
    )
    return summary.round({"pass_at_1": 3, "pass_hat_k": 3, "cost_per_task": 5, "steps_per_task": 2})
