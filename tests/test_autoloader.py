from pathlib import Path

import pytest

from slingshot_autoloader import SlingshotAutoLoaderMode
from slingshot_autoloader_config import AutoloaderConfig, AutoloadMainConfig

pytestmark = pytest.mark.usefixtures("monkeypatch_ocio_config_path")


@pytest.mark.parametrize(
    "source_path, search_path, version_regex, expected_path",
    [
        pytest.param(
            Path("./version_1.2.3/file.txt"),
            "file.txt",
            None,
            Path("./version_1.2.3/file.txt"),
            id="happy_path_simple",
        ),
        pytest.param(
            Path("./version_1.2.3/file.txt"),
            "f*.txt",
            None,
            Path("./version_1.2.3/file.txt"),
            id="happy_path_wildcard",
        ),
        pytest.param(
            Path("./path/file_v001.txt"),
            "*${version}.txt",
            None,
            Path("./path/file_v001.txt"),
            id="happy_path_with_version_regex",
        ),
        pytest.param(
            Path("./path/file_version1.2.3.txt"),
            "*${version}.txt",
            r"version(?P<version>[0-9]+\.[0-9]+\.[0-9]+)",
            Path("./path/file_version1.2.3.txt"),
            id="happy_path_with_version_regex2",
        ),
        pytest.param(
            Path("./version_1.2.3/file.txt"),
            "*.txt",
            None,
            Path("./version_1.2.3/file.txt"),
            id="happy_path_glob",
        ),
        pytest.param(
            Path("./version_1.2.3/file.txt"),
            "*.mov",
            None,
            None,
            id="happy_path_nomatch",
        ),
    ],
)
def test_find_file_happy_path(
    source_path: Path,
    search_path: str,
    version_regex: str,
    expected_path: Path,
    tmp_path: Path,
):
    # Arrange
    source_path = tmp_path / source_path
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.touch()

    autoloader = SlingshotAutoLoaderMode()
    if version_regex:
        autoloader.config = AutoloaderConfig(
            main=AutoloadMainConfig(version_regex=version_regex)
        )

    # Act
    result = autoloader._find_file(source_path, search_path)

    # Assert
    assert result == (tmp_path / expected_path if expected_path else None)
