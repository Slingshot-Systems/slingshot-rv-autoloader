import os
import re
from configparser import ConfigParser
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from slingshot_autoloader_config import (
    AutoloadColorConfig,
    AutoloaderConfig,
    AutoloadMainConfig,
    AutoloadPlatesConfig,
    _create_default_config,
    _read_config,
    get_ocio_config,
    load_or_create_config,
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
                    "mov_colorspace": "Rec709",
                    "exr_colorspace": "ACES2065-1",
                    "working_space": "ACEScc",
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
                    mov_colorspace="Rec709",
                    exr_colorspace="ACES2065-1",
                    working_space="ACEScc",
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
                color=AutoloadColorConfig(look_cdl=None, look_lut=None),
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
                    "mov_colorspace": "Rec709",
                    "exr_colorspace": "colorspace-1",
                    "working_space": "colorspace-2",
                    "look_cdl": "/path/to/look_cdl",
                    "look_lut": "/path/to/look_lut",
                },
            },
            AutoloaderConfig(
                color=AutoloadColorConfig(
                    mov_colorspace="Rec709",
                    exr_colorspace="colorspace-1",
                    working_space="colorspace-2",
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
                "color": {},
            },
            AutoloaderConfig(
                plates=AutoloadPlatesConfig(
                    plate_mov_path="/path/to/plate_mov",
                    plate_frames_path=None,
                    plate_first_frame_in_file=None,
                    plate_cut_in_frame=None,
                ),
                color=AutoloadColorConfig(
                    mov_colorspace="Rec709",
                    exr_colorspace="ACES2065-1",
                    working_space="ACEScc",
                    look_cdl=None,
                    look_lut=None,
                ),
            ),
            id="edge_case_missing_some_keys",
        ),
    ],
)
@patch("slingshot_autoloader_config.Path.exists", return_value=True)
def test_load_or_create_config_exists(
    mock_exists: Mock, config_data, expected_settings
):
    # Arrange
    _config = ConfigParser(allow_no_value=True)
    _config.optionxform = str  # type: ignore
    _config.read_dict(config_data)

    with patch(
        "slingshot_autoloader_config._read_config",
        return_value=_config,
    ):
        # Act
        if isinstance(expected_settings, type) and issubclass(
            expected_settings, Exception
        ):
            with pytest.raises(expected_settings):
                load_or_create_config()
        else:
            result = load_or_create_config()

            # Assert
            assert result == expected_settings


@patch("slingshot_autoloader_config.Path.exists", return_value=False)
def test_load_or_create_config_does_not_exist(mock_exists: Mock):
    config = load_or_create_config()
    assert config == AutoloaderConfig()


@patch("slingshot_autoloader_config.get_config_path")
def test_load_or_create_config_invalid_config_file(
    mock_get_config_path: Mock, tmp_path: Path
):
    config = tmp_path / "invalid_config.cfg"
    config.write_text("totally invalid file")
    mock_get_config_path.return_value = config

    assert load_or_create_config() == AutoloaderConfig()


def test__create_default_config(tmp_path: Path):
    config_path = tmp_path / "new_config.cfg"
    config = _create_default_config(config_path)
    print(config.__dict__)

    assert config_path.is_file()
    default_config = AutoloaderConfig()
    for section in config.sections():
        for key in config[section]:
            assert config[section][key] == getattr(
                getattr(default_config, section), key
            )


def test__read_config(tmp_path: Path):
    config_file = tmp_path / "test_config.ini"

    # Create an .ini file with the provided settings
    settings = {"sectioN1": {"kEy1": "vAlue1"}}
    config = ConfigParser()
    config.optionxform = str  # type: ignore
    for section, keys in settings.items():
        config[section] = keys

    with config_file.open("w") as f:
        config.write(f)

    # Read and verify settings from the .ini file
    disk_config = _read_config(config_file)
    for section, keys in settings.items():
        assert disk_config.has_section(section)
        for key, value in keys.items():
            assert disk_config.get(section, key) == value
        for key, value in disk_config[section].items():
            assert key in keys


OCIO_CONFIG_PATH = (
    Path(__file__).parent.parent
    / "src/ocio/studio-config-v2.1.0_aces-v1.3_ocio-v2.2.ocio"
)


@pytest.mark.parametrize(
    "working_space, exr_colorspace, expected_working_space, expected_exr_colorspace",
    [
        pytest.param(
            "lin_srgb",
            "lin_ap1",
            "Linear Rec.709 (sRGB)",
            "ACEScg",
            id="happy_path_lin_srgb",
        ),
        pytest.param(
            "ACES - ACES2065-1",
            "ACEScc",
            "ACES2065-1",
            "ACEScc",
            id="happy_path_aces",
        ),
        pytest.param(
            '"ARRI LogC4"',
            '"Linear ARRI Wide Gamut 4"',
            "ARRI LogC4",
            "Linear ARRI Wide Gamut 4",
            id="happy_path_extra_quotes",
        ),
    ],
)
@pytest.mark.usefixtures("monkeypatch_ocio_config_path")
def test_get_ocio_config_happy_path(
    working_space: str,
    exr_colorspace: str,
    expected_working_space: str,
    expected_exr_colorspace: str,
):
    autoloader_config = AutoloaderConfig(
        color=AutoloadColorConfig(
            working_space=working_space, exr_colorspace=exr_colorspace
        )
    )

    # Act
    get_ocio_config(autoloader_config)
    assert os.environ["OCIO"] == OCIO_CONFIG_PATH.as_posix()

    # Assert
    assert autoloader_config.color.working_space == expected_working_space
    assert autoloader_config.color.exr_colorspace == expected_exr_colorspace


@pytest.mark.usefixtures("monkeypatch_ocio_config_path")
@pytest.mark.parametrize(
    "working_space, exr_colorspace, expected_exception",
    [
        pytest.param(
            "invalid_working_space", "lin_srgb", Exception, id="invalid_working_space"
        ),
        pytest.param(
            "lin_srgb", "invalid_exr_colorspace", Exception, id="invalid_exr_colorspace"
        ),
        pytest.param(
            "invalid_working_space",
            "invalid_exr_colorspace",
            Exception,
            id="invalid_both",
        ),
    ],
)
@pytest.mark.usefixtures("monkeypatch_ocio_config_path")
def test_get_ocio_config_invalid_colorspace(
    working_space: str,
    exr_colorspace: str,
    expected_exception: type[Exception],
):
    autoloader_config = AutoloaderConfig(
        color=AutoloadColorConfig(
            working_space=working_space, exr_colorspace=exr_colorspace
        )
    )

    with pytest.raises(
        expected_exception,
        match=re.escape("Configuration error: Could not find color space:"),
    ):
        get_ocio_config(autoloader_config)


@patch("slingshot_autoloader_config.Path.exists", return_value=False)
def test_get_ocio_config_file_not_found(mock_exists: Mock):
    ocio_path = (
        Path(__file__).parent.parent
        / "SupportFiles"
        / "slingshot_autoloader"
        / "ocio/studio-config-v2.1.0_aces-v1.3_ocio-v2.2.ocio"
    )
    autoloader_config = AutoloaderConfig()
    del os.environ["OCIO"]

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        get_ocio_config(autoloader_config)

    assert str(exc_info.value) == (
        f"OCIO config file not found at path: {ocio_path.as_posix()}"
    )
