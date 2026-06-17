import pytest
from pathlib import Path

from git_tutorial.sandbox import GitSandbox
from git_tutorial.content import discover_phases, CONTENT_DIR


@pytest.fixture
def sandbox():
    sb = GitSandbox()
    yield sb
    sb.cleanup()


@pytest.fixture
def sandbox_with_remote():
    sb = GitSandbox()
    sb.setup_remote()
    yield sb
    sb.cleanup()


@pytest.fixture
def phases():
    return discover_phases()


@pytest.fixture
def content_dir():
    return CONTENT_DIR
