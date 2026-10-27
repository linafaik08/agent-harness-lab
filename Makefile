PYTHON := .venv/bin/python
# Python resolves the model exactly as the notebook does (shell first, then .env),
# so the results folder below always matches the run.
MODEL := $(shell $(PYTHON) -c "from agent_harness_lab.models import DEFAULT_MODEL; print(DEFAULT_MODEL)" 2>/dev/null)

.PHONY: install test demo full analyze clean

install:  ## Create .venv and install the project with its dependencies
	uv venv .venv --python 3.11 --allow-existing
	uv pip install --python $(PYTHON) -e .

test:  ## Run the test suite (task integrity, grading, OpenAI client, metrics, trace flags); no API calls
	$(PYTHON) -m pytest -q

demo:  ## Execute the notebook in place on 3 tasks (54 trials, about $1)
	$(PYTHON) scripts/run_notebook.py
	$(PYTHON) scripts/export_chart.py results/$(MODEL)_3tasks

full:  ## All 10 tasks (180 trials, about $1.50 to $4); results in results/<model>_10tasks/
	HARNESS_TASKS=all $(PYTHON) scripts/run_notebook.py --output results/$(MODEL)_10tasks/harness_ladder.ipynb
	$(PYTHON) scripts/export_chart.py results/$(MODEL)_10tasks

analyze:  ## Flag test edits, grader reads and loops; RUN=results/<run> picks the run
	$(PYTHON) scripts/analyze_traces.py $(or $(RUN),results/$(MODEL)_10tasks) --details

clean:  ## Remove caches and saved transcripts (keeps trials, summaries and charts)
	rm -rf .pytest_cache results/*/transcripts
	find . -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
