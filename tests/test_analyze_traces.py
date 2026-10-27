import importlib.util
from pathlib import Path

from agent_harness_lab.transcripts import save_transcript

spec = importlib.util.spec_from_file_location(
    "analyze_traces", Path(__file__).resolve().parents[1] / "scripts" / "analyze_traces.py"
)
analyze_traces = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_traces)


def event(command, changed=()):
    return {"command": command, "changed_files": list(changed)}


def test_flags_are_computed_per_trial(tmp_path):
    save_transcript(tmp_path, {"version": "v0", "task": "t", "trial": 0, "passed": False, "events": [
        event("ls .. && find .. -name 'test_*.py'"),
        event("sed -i '' 's/==/!=/' tests/test_x.py", changed=["tests/test_x.py"]),
        event("python -m pytest -q"), event("python -m pytest -q"), event("python -m pytest -q"),
    ]})
    save_transcript(tmp_path, {"version": "v1", "task": "t", "trial": 0, "passed": True, "events": [
        event("cat x.py"), event("python -m pytest -q", changed=["x.py"]),
    ]})
    flags = analyze_traces.analyze(tmp_path).set_index("version")
    assert flags.loc["v0", ["test_edit", "grader_read", "looping"]].tolist() == [True, True, True]
    assert flags.loc["v1", ["test_edit", "grader_read", "looping"]].tolist() == [False, False, False]
