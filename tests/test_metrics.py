import pandas as pd

from agent_harness_lab.metrics import summarize


def test_pass_at_1_and_pass_hat_k():
    rows = [
        # Task a passes every trial, task b passes one trial in three.
        *({"version": "v0", "task": "a", "passed": True, "cost_usd": 0.01, "steps": 4} for _ in range(3)),
        {"version": "v0", "task": "b", "passed": True, "cost_usd": 0.03, "steps": 8},
        {"version": "v0", "task": "b", "passed": False, "cost_usd": 0.03, "steps": 8},
        {"version": "v0", "task": "b", "passed": False, "cost_usd": 0.03, "steps": 8},
    ]
    summary = summarize(pd.DataFrame(rows)).loc["v0"]
    assert summary["pass_at_1"] == round((1 + 1 / 3) / 2, 3)
    assert summary["pass_hat_k"] == 0.5
    assert summary["cost_per_task"] == 0.02
    assert summary["steps_per_task"] == 6
    assert summary["k"] == 3
