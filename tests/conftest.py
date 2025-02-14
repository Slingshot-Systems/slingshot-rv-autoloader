from pathlib import Path

import pytest

import slingshot_autoloader_config


@pytest.fixture
def monkeypatch_ocio_config_path(monkeypatch: pytest.MonkeyPatch):
    mock_support_files_path = Path(__file__).parent.parent / "src"
    monkeypatch.setattr(
        slingshot_autoloader_config,
        "SUPPORT_FILES_PATH",
        mock_support_files_path,
    )
