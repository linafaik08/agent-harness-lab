# Agent harness lab

## Goal
Show, with one fixed model and ten small bug-fix tasks, how far the score moves when only the
harness around the model changes. "Done" means: `make test` passes without any API call,
`make demo` executes `notebooks/harness_ladder.ipynb` end to end on three tasks against
`gpt-6-luna`, `make full` writes per-trial results for all ten tasks to
`results/gpt-6-luna_10tasks/`, and the README shows the resulting chart. Every run that calls
the API happens only after explicit approval.

## Current state
The repository was empty at the start. The local interpreter is Python 3.11 with
`openai==0.27.2` installed globally, which predates the 1.x client, so the project pins its own
dependencies in a local virtual environment created by `uv`.

## Approach
**One notebook owns the story.** `notebooks/harness_ladder.ipynb` contains the agent loop
(about 100 lines), one cell per harness component, one cell per version, the runs and the
chart. Components share a small hook interface (`system_prompt`, `context_note`, `on_output`,
`on_finish`, `after_step`, `should_stop`), so the loop stays unchanged while versions are lists
of components: v0 is `[]`, v1 adds `AgentsMap`, v2 adds `TestGate`, v3 adds `LoopDetector` and
`Budget`, v4 adds `ConciseOutput`, v5 adds `ProgressFile`.

**Plumbing lives in `src/agent_harness_lab/`.** It holds the OpenAI client, task loading and
workspace copies, shell execution with a timeout, workspace snapshots used to detect which
files a command changed, hidden-test grading, transcript saving and the metric computation.

**The model is called through the Responses API.** The GPT-6 models only combine reasoning
with tool calls through that API. Requests are stateless, with the encrypted reasoning
replayed on later turns. The loop keeps its history in the chat-completions format, which is
easier to read in transcripts, and `OpenAIClient` translates at the boundary.

**The base loop keeps a short context window.** It always keeps the system prompt and the
task, plus the most recent messages. This mirrors real context limits and is what gives the
progress file something to fix.

**Alternatives rejected.** An eval framework (Inspect, SWE-bench harness) and Docker isolation
were excluded by the brief. Putting the loop in `src/` would hide the part the reader is meant
to study. A simulated model was built and then removed: it made runs free, but its failure
modes were chosen by hand, so its numbers were partly true by construction and it doubled the
amount of code to explain.

## Reuse
Nothing existed in the repository. The project relies on `openai` (Responses API with tool
calls), `pytest`, `pandas`, `plotly`, `kaleido` (static PNG for the README), `nbconvert` (for
`nbclient` and `nbformat`) and `ipykernel`.

## Steps
1. **Project skeleton.** `pyproject.toml`, `Makefile`, `.gitignore`, `src/agent_harness_lab/__init__.py`.
2. **Tasks.** `tasks/<id>/repo/` (tiny module plus one failing visible test),
   `tasks/<id>/hidden/test_hidden.py` (grader, never copied into the workspace),
   `tasks/<id>/task.json` (issue text, plus the reference fix used only by the tests).
3. **Plumbing.** `tasks.py`, `workspace.py`, `grading.py`, `models.py`, `transcripts.py`,
   `metrics.py`.
4. **Notebook.** Loop, components, versions, run, save, chart. Reads `HARNESS_TASKS`
   (default `3`) from the environment and writes to `results/<model>_<n>tasks/`.
5. **Scripts.** `analyze_traces.py` flags test edits (from the recorded file diffs), grader
   reads and looping; `run_notebook.py` executes the notebook headlessly; `export_chart.py`
   renders the PNG outside the kernel, where Kaleido exports were observed to stall.
6. **Tests.** Task integrity, grading, the Responses translation against the SDK's own types,
   metrics and trace flags, all without network access.
7. **README and chart.** After an approved `make full`, the chart and summary table go into
   the README.

## Risks and edge cases
- **The model's shell commands run on this machine.** There is no sandbox by design; the
  workspace is a temp copy and every command has a timeout, but nothing stops `rm -rf ~`. The
  README says so before the run commands.
- **The Responses client is untested against the live API.** The tests check the request shape
  and the cost arithmetic with stubbed responses; the first `make demo` is the real check.
- **Hidden tests import from the workspace.** They run with `PYTHONPATH` set to the workspace
  and a working directory outside it, so a test the agent edited cannot shadow them.
- **Cost.** A full run is 180 trials; at about 14M input tokens, `gpt-6-luna` costs $1.50 to
  $4 depending on reasoning tokens. v0 to v2 have no budget beyond the 30-step safety cap.

## Testing
`tests/` uses pytest: task integrity, grading, the OpenAI client with stubbed responses,
metrics on a hand-built table, and trace flags on synthetic transcripts. `make demo` is the
end-to-end check and costs about a dollar.

## Out of scope
Sandboxing, parallel trial execution, other model providers, a free offline mode, statistical
significance tests and any eval framework.

## Revision log
- Round 1: removed the simulated model and mock mode, so every run uses `gpt-6-luna` and the README waits for a real run.
