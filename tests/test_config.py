from configparser import ConfigParser
from pathlib import Path
from unittest.mock import patch

import pytest

from src.slingshot_autoloader_config import (
    AutoloadColorConfig,
    AutoloaderConfig,
    AutoloadMainConfig,
    AutoloadPlatesConfig,
    get_or_create_default_config,
    read_settings,
)


@pytest.mark.parametrize(
    "config_data, expected_settings",
    [
        pytest.param(
            {
                "main": {
                    "version_regex": "test_regex",
                },
                "plates": {
                    "plate_mov_path": "/path/to/plate_mov",
                    "plate_frames_path": "/path/to/plate_frames",
                    "plate_first_frame_in_file": 5,
                    "plate_cut_in_frame": 1000,
                },
                "other": {
                    "v000": "/path/to/v000_mov",
                    "v000_Frames": "/path/to/v000_frames",
                    "prores": r"./*${version}_prores.mov",
                },
                "color": {
                    "file_lut": "/path/to/file_lut",
                    "look_cdl": "/path/to/look_cdl",
                    "look_lut": "/path/to/look_lut",
                },
            },
            AutoloaderConfig(
                main=AutoloadMainConfig(version_regex="test_regex"),
                plates=AutoloadPlatesConfig(
                    plate_mov_path="/path/to/plate_mov",
                    plate_frames_path="/path/to/plate_frames",
                    plate_first_frame_in_file=5,
                    plate_cut_in_frame=1000,
                ),
                other={
                    "v000": "/path/to/v000_mov",
                    "v000_Frames": "/path/to/v000_frames",
                    "prores": r"./*${version}_prores.mov",
                },
                color=AutoloadColorConfig(
                    file_lut="/path/to/file_lut",
                    look_cdl="/path/to/look_cdl",
                    look_lut="/path/to/look_lut",
                ),
            ),
            id="happy_path_all_keys_present",
        ),
        pytest.param(
            {
                "plates": {
                    "plate_mov_path": None,
                    "plate_frames_path": None,
                    "v000_mov_path": None,
                    "v000_frames_path": None,
                    "plate_first_frame_in_file": None,
                    "plate_cut_in_frame": None,
                },
                "other": {
                    "v000": None,
                    "v000_Frames": None,
                    "prores": None,
                },
                "color": {
                    "file_lut": None,
                    "look_cdl": None,
                    "look_lut": None,
                },
            },
            AutoloaderConfig(
                main=AutoloadMainConfig(version_regex=r"_(?P<version>v\d+)"),
                plates=AutoloadPlatesConfig(
                    plate_mov_path=None,
                    plate_frames_path=None,
                    plate_first_frame_in_file=None,
                    plate_cut_in_frame=None,
                ),
                other={},
                color=AutoloadColorConfig(
                    file_lut=None,
                    look_cdl=None,
                    look_lut=None,
                ),
            ),
            id="all_none_values",
        ),
        pytest.param(
            {
                "plates": {
                    "plate_mov_path": "/path/to/plate_mov",
                    "plate_frames_path": "/path/to/plate_frames",
                    "plate_first_frame_in_file": 5,
                    "plate_cut_in_frame": 1000,
                }
            },
            AutoloaderConfig(
                plates=AutoloadPlatesConfig(
                    plate_mov_path="/path/to/plate_mov",
                    plate_frames_path="/path/to/plate_frames",
                    plate_first_frame_in_file=5,
                    plate_cut_in_frame=1000,
                )
            ),
            id="plates_only",
        ),
        pytest.param(
            {
                "color": {
                    "file_lut": "/path/to/file_lut",
                    "look_cdl": "/path/to/look_cdl",
                    "look_lut": "/path/to/look_lut",
                },
            },
            AutoloaderConfig(
                color=AutoloadColorConfig(
                    file_lut="/path/to/file_lut",
                    look_cdl="/path/to/look_cdl",
                    look_lut="/path/to/look_lut",
                )
            ),
            id="color_only",
        ),
        pytest.param(
            {},
            AutoloaderConfig(plates=AutoloadPlatesConfig()),
            id="edge_case_missing_all_sections",
        ),
        pytest.param(
            {
                "plates": {
                    "plate_mov_path": "/path/to/plate_mov",
                },
                "color": {
                    "file_lut": "/path/to/file_lut",
                },
            },
            AutoloaderConfig(
                plates=AutoloadPlatesConfig(
                    plate_mov_path="/path/to/plate_mov",
                    plate_frames_path=None,
                    plate_first_frame_in_file=None,
                    plate_cut_in_frame=None,
                ),
                color=AutoloadColorConfig(
                    file_lut="/path/to/file_lut",
                ),
            ),
            id="edge_case_missing_some_keys",
        ),
    ],
)
def test_read_settings(config_data, expected_settings):
    # Arrange
    _config = ConfigParser(allow_no_value=True)
    _config.optionxform = str  # type: ignore
    _config.read_dict(config_data)

    with patch(
        "src.slingshot_autoloader_config.get_or_create_default_config",
        return_value=_config,
    ):
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
            {"section1": {"key1": "value1"}, "sEction2": {"kEy2": "vAlue2"}},
            ["section1", "sEction2"],
            id="create_default_config",
        ),
        pytest.param(False, {}, [], id="create_empty_default_config"),
        pytest.param(
            True,
            {"sectioN1": {"kEy1": "vAlue1"}},
            ["sectioN1"],
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
        config.optionxform = str  # type: ignore
        for section, keys in settings.items():
            config[section] = keys

        with config_file.open("w") as f:
            config.write(f)

    with patch(
        "src.slingshot_autoloader_config.get_config_path", return_value=config_file
    ):
        config = get_or_create_default_config()
        print(config.__dict__)

        # Assert
        if config_exists:
            # Check if default config was created
            for section, keys in settings.items():
                assert config.has_section(section)
                for key, value in keys.items():
                    assert config.get(section, key) == value
                for key, value in config[section].items():
                    assert key in keys
        else:
            # Check if existing config was read
            default_config = AutoloaderConfig()
            for section in config.sections():
                for key in config[section]:
                    assert config[section][key] == getattr(
                        getattr(default_config, section), key
                    )
