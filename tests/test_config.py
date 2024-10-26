from configparser import ConfigParser
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import (
    AutoloadPlatesConfig,
    Settings,
    get_or_create_default_config,
    read_settings,
)


@pytest.mark.parametrize(
    "config_data, expected_settings",
    [
        pytest.param(
            {
                "plates": {
                    "plate_mov_path": "/path/to/plate_mov",
                    "plate_frames_path": "/path/to/plate_frames",
                    "v000_mov_path": "/path/to/v000_mov",
                    "v000_frames_path": "/path/to/v000_frames",
                    "plate_first_frame_in_file": 5,
                    "plate_cut_in_frame": 1000,
                }
            },
            Settings(
                plates=AutoloadPlatesConfig(
                    plate_mov_path="/path/to/plate_mov",
                    plate_frames_path="/path/to/plate_frames",
                    v000_mov_path="/path/to/v000_mov",
                    v000_frames_path="/path/to/v000_frames",
                    plate_first_frame_in_file=5,
                    plate_cut_in_frame=1000,
                )
            ),
            id="happy_path_all_keys_present",
        ),
        pytest.param(
            {},
            Settings(plates=AutoloadPlatesConfig()),
            id="edge_case_missing_plates_section",
        ),
        pytest.param(
            {
                "plates": {
                    "plate_mov_path": "/path/to/plate_mov",
                }
            },
            Settings(
                plates=AutoloadPlatesConfig(
                    plate_mov_path="/path/to/plate_mov",
                    plate_frames_path=None,
                    v000_mov_path=None,
                    v000_frames_path=None,
                    plate_first_frame_in_file=None,
                )
            ),
            id="edge_case_missing_some_keys",
        ),
    ],
)
def test_read_settings(config_data, expected_settings):
    # Arrange
    _config = ConfigParser(allow_no_value=True)
    _config.read_dict(config_data)

    with patch("src.config.get_or_create_default_config", return_value=_config):
        # Act
        if isinstance(expected_settings, type) and issubclass(
            expected_settings, Exception
        ):
            with pytest.raises(expected_settings):
                read_settings()
        else:
            result = read_settings()

            # Assert
            assert result == expected_settings


@pytest.mark.parametrize(
    "config_exists, settings, expected_sections",
    [
        pytest.param(
            False,
            {"section1": {"key1": "value1"}, "section2": {"key2": "value2"}},
            ["section1", "section2"],
            id="create_default_config",
        ),
        pytest.param(False, {}, [], id="create_empty_default_config"),
        pytest.param(
            True,
            {"section1": {"key1": "value1"}},
            ["section1"],
            id="read_existing_config",
        ),
    ],
)
def test_get_or_create_default_config(
    tmp_path: Path,
    config_exists: bool,
    settings: dict[str, dict[str, str]],
    expected_sections: list[str],
):
    # Arrange
    config_file = tmp_path / "test_config.ini"

    if config_exists:
        # Create an actual .ini file with the provided settings
        config = ConfigParser()
        for section, keys in settings.items():
            config[section] = keys

        with config_file.open("w") as f:
            config.write(f)

    with patch("src.config.get_config_path", return_value=config_file):
        config = get_or_create_default_config()
        print(config.__dict__)

        # Assert
        if config_exists:
            # Check if default config was created
            for section, keys in settings.items():
                assert config.has_section(section)
                for key, value in keys.items():
                    assert config.get(section, key) == value
        else:
            # Check if existing config was read
            default_config = Settings()
            for section in config.sections():
                for key in config[section]:
                    assert config[section][key] == getattr(
                        getattr(default_config, section), key
                    )
