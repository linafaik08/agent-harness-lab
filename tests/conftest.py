import pytest

from agent_harness_lab.tasks import load_tasks


@pytest.fixture(scope="session")
def tasks():
    return load_tasks()
