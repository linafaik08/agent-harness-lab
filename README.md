# agent-harness-lab

A small lab showing how much an agent's score depends on the harness around the model. The
model stays fixed while the harness grows one component at a time, from a bare bash loop to a
harness with a repository map, a test gate, a loop detector, a budget, concise output and a
progress file. Each version runs on ten tiny bug-fix tasks, three trials each, and is graded
by hidden tests the agent never sees.

Everything lives in plain Python and pytest. There is no Docker, no sandbox framework and no
eval framework. The story is told in a single notebook,
[notebooks/harness_ladder.ipynb](notebooks/harness_ladder.ipynb).

> **Results.** No run has been recorded yet. After `make full`, the chart is saved to
> `results/gpt-6-luna_10tasks/ladder.png` and belongs here, together with the table from
> `summary.csv`.

## The ladder

Each version keeps everything from the previous one and adds a single component.

| Version | Added component | What it does |
|---|---|---|
| v0 | bare loop | A system prompt, one `bash` tool and a short context window. |
| v1 | `AGENTS.md` map | Names the source files and the test command, and states that tests are never edited. |
| v2 | test gate | Refuses "done" until the tests have run since the last change to the workspace. |
| v3 | loop detector, budget | Nudges and then stops an agent repeating a no-op command; caps steps (20) and cost ($0.05) per trial. |
| v4 | concise output | Drops blank lines and keeps the head and tail of long outputs. |
| v5 | progress file | The agent keeps `PROGRESS.md`, and the harness pins it into every step. |

Four numbers describe each version:

- **pass@1** is the share of trials that passed, averaged over tasks. It estimates the chance
  that one attempt succeeds.
- **pass^3** is the share of tasks on which all three trials passed. It measures reliability
  rather than capability.
- **Cost and steps** are averaged over every trial. A step is one model call, and the cost is
  the billed price of its tokens, reasoning and caching included.

## Quick start

The project needs Python 3.10+ and [uv](https://docs.astral.sh/uv/). Every run calls the
OpenAI API and costs money; the test suite does not.

```bash
make install          # creates .venv and installs the project
make test             # task integrity, grading, OpenAI client, metrics, trace flags
cp .env.example .env  # then paste your key after OPENAI_API_KEY=
make demo             # 3 tasks, 54 trials, about $1, notebook executed in place
make full             # 10 tasks, 180 trials, about $1.50 to $4
make analyze          # flags test edits, grader reads and loops (RUN=results/<run>)
```

Settings live in `.env`, which git ignores: `OPENAI_API_KEY`, plus the optional `OPENAI_MODEL`
(default `gpt-6-luna`) and `OPENAI_REASONING_EFFORT` (default `low`; one of `none`, `minimal`,
`low`, `medium`, `high`, `xhigh`, `max`). A variable set in the shell takes precedence over
`.env`, so `OPENAI_MODEL=gpt-6-sol make full` works for a one-off run.

The notebook also runs interactively with the `.venv` kernel. `HARNESS_TASKS` sets the number
of tasks (a number or `all`, default `3`). Each run writes to its own folder,
`results/<model>_<n>tasks/`:

| File | Content |
|---|---|
| `trials.csv` | One row per trial: version, task, trial, passed, stop reason, steps, cost, tokens. |
| `summary.csv` | One row per version with the four metrics. |
| `ladder.html`, `ladder.json` | The interactive chart and its saved figure, built from `trials.csv`. |
| `ladder.png` | The static chart, rendered from `ladder.json` by `scripts/export_chart.py`, which the Makefile runs after every run. |
| `transcripts/<version>/<task>/trial_<n>.json` | Full message history, per-command events (exit code, output size, files changed) and grader output. |

## Cost

A full run makes 180 trials (6 versions x 10 tasks x 3 trials). The estimate assumes about
2,500 steps and 14 million input tokens, the volume of a dry run of the same ladder; a real
model may take more or fewer steps. At that volume `gpt-6-luna` costs about **$1.50**
without reasoning, **$2.10** at 500 reasoning tokens per step and **$4** at 2,000. Reasoning
tokens are billed as output, so the effort setting moves the bill most.

Nearly 90% of the tokens go to v0 to v2, which are bounded only by the 30-step safety cap. At
Luna's prices the $0.05 cost cap of v3 to v5 rarely binds, and the 20-step cap does the work.
The prices in `PRICES_PER_MILLION` come from OpenAI's pricing page in October 2026 and deserve
a check before a run.

## The OpenAI client

The client calls the Responses API, which the GPT-6 models require to combine reasoning with
tool calls. Requests are stateless (`store=False`): the loop keeps the history, and the model's
encrypted reasoning is replayed with its own turns. The loop and the transcripts keep the
simpler chat-completions message format, and `OpenAIClient` translates at the boundary.

> **Warning.** The model's shell commands run on your machine, with your permissions. Each
> trial works in a temporary copy of the task, and every command has a 30-second timeout, but
> nothing is sandboxed: a command can read or delete anything your user can. Running it inside
> a disposable VM or container is the prudent choice.

## How a trial works

1. **Workspace.** The task's `repo/` is copied into a fresh temporary directory. The hidden
   tests stay in the task folder, outside the copy.
2. **Loop.** The agent receives the issue and a `bash` tool. At every step it sees the system
   prompt, the task, any pinned notes and the last 12 messages. Each command runs in the copy
   with a timeout, and the loop records which files it changed.
3. **Stop.** The trial ends when the agent replies without a command and no component objects,
   or when a component stops it (loop, budget), or at the 30-step safety cap.
4. **Grade.** The hidden tests run from an empty directory with the workspace on `PYTHONPATH`,
   so an edited copy of the visible tests has no influence on the verdict.
5. **Save.** The transcript is written to disk and the copy is deleted.

## Repository layout

```
notebooks/harness_ladder.ipynb   agent loop, one cell per component, runs and chart
src/agent_harness_lab/
    tasks.py          task loading and temporary workspaces
    workspace.py      shell commands with a timeout, workspace snapshots and diffs
    models.py         OpenAI Responses client and prices
    grading.py        hidden-test grading
    transcripts.py    transcript saving and loading
    metrics.py        pass@1, pass^k, cost and steps per version
scripts/
    analyze_traces.py flags test edits, grader reads and loops in saved transcripts
    run_notebook.py   executes the notebook headlessly (used by the Makefile)
    export_chart.py   renders a run's ladder.json to ladder.png outside the notebook kernel
tasks/<id>/
    repo/             the tiny repository: one module, one failing test, sample data
    hidden/           the grader's tests, never copied into the workspace
    task.json         issue text and the reference fix (read only by the tests)
tests/                the lab's own test suite
docs/PLAN.md          the implementation plan
```

## The tasks

Ten original bugs, each small enough to fix in one edit: `slugify` leaving stray hyphens,
`median` on even-length lists, `parse_duration` minutes, `chunked` dropping the last chunk,
case-sensitive `word_count`, `merge_intervals` on unsorted input, subtractive Roman numerals,
one-level `flatten`, `moving_average` missing its final window and order-scrambling `dedupe`.
Each repository also carries a sample-data file of about 15 KB, which is harmless to the fix
but costly to read in full. The test suite checks that every task fails as shipped and passes
with its reference fix, on both the visible and the hidden tests.
