import atexit
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import slingshot_autoloader_config


def setup_rv_mocks():
    """The rv module isn't available in our testing environment (outside of RV).
    Let's create mock modules for rv, rv.commands, rv.extra_commands, and rv.rvtypes."""

    # Create mock modules
    mock_rv = MagicMock()
    mock_commands = MagicMock()
    mock_extra_commands = MagicMock()
    mock_rvtypes = MagicMock()

    # Set up MinorMode as a proper class that can be inherited from
    class MockMinorMode:
        def __init__(self):
            pass

        def init(self, *args, **kwargs):
            pass

    # Make MinorMode available on the mock
    mock_rvtypes.MinorMode = MockMinorMode

    # Create the module structure
    mock_rv.commands = mock_commands
    mock_rv.extra_commands = mock_extra_commands
    mock_rv.rvtypes = mock_rvtypes

    # Add to sys.modules directly
    sys.modules["rv"] = mock_rv
    sys.modules["rv.commands"] = mock_commands
    sys.modules["rv.extra_commands"] = mock_extra_commands
    sys.modules["rv.rvtypes"] = mock_rvtypes


def cleanup_rv_mocks():
    """Remove mock modules from sys.modules."""
    for name in ["rv", "rv.commands", "rv.extra_commands", "rv.rvtypes"]:
        if name in sys.modules:
            del sys.modules[name]


# Set up mocks immediately so they're available for imports in tests
setup_rv_mocks()
# Register cleanup
atexit.register(cleanup_rv_mocks)


@pytest.fixture
def monkeypatch_ocio_config_path(monkeypatch: pytest.MonkeyPatch):
    mock_support_files_path = Path(__file__).parent.parent / "src"
    monkeypatch.setattr(
        slingshot_autoloader_config,
        "SUPPORT_FILES_PATH",
        mock_support_files_path,
    )
