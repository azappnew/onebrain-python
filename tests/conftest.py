import sys
import os

import pytest

# Ensure the src directory is on the path so we can import submodules
# directly without triggering the top-level __init__.py re-exports (which
# reference modules that may not exist yet in the repo).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from onebrain._client import BaseClient  # noqa: E402


@pytest.fixture
def api_key():
    return "ob_test_key_12345"


@pytest.fixture
def base_url():
    return "https://api.onebrain.ai"


@pytest.fixture
def client(api_key, base_url):
    return BaseClient(api_key=api_key, base_url=base_url)
