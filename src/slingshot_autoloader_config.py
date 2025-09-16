# Copyright (C) 2025 Slingshot Systems Inc.
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import shutil
from configparser import ConfigParser
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Literal

import PyOpenColorIO as OCIO

logger = logging.getLogger(__name__)
logger = logging.getLogger("SlingshotAutoLoader")

SUPPORT_FILES_PATH = (
    Path(__file__).parent.parent / "SupportFiles" / "slingshot_autoloader"
)


@dataclass(frozen=True)
class AutoloadMainConfig:
    version_regex: str = r"_(?P<version>v\d+)"


@dataclass(frozen=True)
class AutoloadPlatesConfig:
    plate_mov_path: str | None = None
    plate_frames_path: str | None = None
    plate_cut_in_frame: int | None = None
    plate_first_frame_in_file: int | None = None


@dataclass
class AutoloadColorConfig:
    mov_colorspace: Literal["sRGB", "Rec709", "Linear"] = "Rec709"
    exr_colorspace: str = "ACES2065-1"
    working_space: str = "ACEScc"
    look_cdl: str | None = None
    look_lut: str | None = None


@dataclass(frozen=True)
class AutoloaderConfig:
    main: AutoloadMainConfig = field(default_factory=AutoloadMainConfig)
    plates: AutoloadPlatesConfig = field(default_factory=AutoloadPlatesConfig)
    other: dict[str, str] = field(default_factory=dict)
    color: AutoloadColorConfig = field(default_factory=AutoloadColorConfig)


def _create_default_config(path: Path) -> ConfigParser:
    """Creates a default config file on the disk."""
    config = ConfigParser(allow_no_value=True)
    for datafield, value in asdict(AutoloaderConfig()).items():
        if is_dataclass(value) and not isinstance(value, type):
            _value = asdict(value)
        elif isinstance(value, dict):
            _value = value
        else:
            _value = {}

        config[datafield] = _value

    with open(path, "w") as f:
        config.write(f)

    return config


def _read_config(path: Path) -> ConfigParser:
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str  # don't lowercase keys # type: ignore
    config.read(path)
    return config


def _convert_configparser_to_config(config: ConfigParser) -> AutoloaderConfig:
    return AutoloaderConfig(
        main=AutoloadMainConfig(
            version_regex=config["main"].get("version_regex")
            or AutoloadMainConfig.__dataclass_fields__["version_regex"].default
        )
        if config.has_section("main")
        else AutoloadMainConfig(),
        plates=AutoloadPlatesConfig(
            plate_mov_path=config["plates"].get("plate_mov_path"),
            plate_frames_path=config["plates"].get("plate_frames_path"),
            plate_first_frame_in_file=int(config["plates"]["plate_first_frame_in_file"])
            if config["plates"].get("plate_first_frame_in_file")
            else None,
            plate_cut_in_frame=int(config["plates"]["plate_cut_in_frame"])
            if config["plates"].get("plate_cut_in_frame")
            else None,
        )
        if config.has_section("plates")
        else AutoloadPlatesConfig(),
        other={k: v for k, v in config["other"].items() if v}
        if config.has_section("other")
        else {},
        color=AutoloadColorConfig(
            mov_colorspace=(
                value
                if (value := config["color"].get("mov_colorspace"))
                in ("sRGB", "Rec709", "Linear")
                else AutoloadColorConfig.__dataclass_fields__["mov_colorspace"].default
            ),
            exr_colorspace=config["color"].get("exr_colorspace")
            or AutoloadColorConfig.__dataclass_fields__["exr_colorspace"].default,
            working_space=config["color"].get("working_space")
            or AutoloadColorConfig.__dataclass_fields__["working_space"].default,
            look_cdl=config["color"].get("look_cdl"),
            look_lut=config["color"].get("look_lut"),
        )
        if config.has_section("color")
        else AutoloadColorConfig(),
    )


def get_config_path() -> Path:
    """Gets the path to the config file in the user's home directory."""

    return Path.home() / ".slingshot_rv_autoloader.cfg"


def load_or_create_config() -> AutoloaderConfig:
    config_file = get_config_path()
    if not config_file.exists():
        logger.warning(
            f"Config file not found at path: {config_file.as_posix()}, default settings will be used"
        )
        _config = _create_default_config(config_file)
    else:
        try:
            _config = _read_config(config_file)
        except Exception as e:
            logger.warning(f"Error reading config file: {e}")
            return AutoloaderConfig()

    return _convert_configparser_to_config(_config)


def load_config_from_file(path: Path) -> AutoloaderConfig:
    config = _convert_configparser_to_config(_read_config(path))
    dest_path = get_config_path()
    logger.debug(f"Copying config file {path} to {dest_path}")
    shutil.copy(path, dest_path)
    return config


def get_ocio_config(autoloader_config: AutoloaderConfig) -> OCIO.Config:
    if os.environ.get("OCIO"):
        ocio_config_path = Path(os.environ["OCIO"])
        logger.debug(
            f"Using OCIO config from environment variable: {ocio_config_path.as_posix()}"
        )
    else:
        ocio_config_path = (
            SUPPORT_FILES_PATH / "ocio/studio-config-v2.1.0_aces-v1.3_ocio-v2.2.ocio"
        )

        if not ocio_config_path.exists():
            raise Exception(
                f"OCIO config file not found at path: {ocio_config_path.as_posix()}"
            )

        # we don't use this at all, but it's required to suppress the "ERROR: OCIO environment variable not set" error when creating an ocio node
        # https://github.com/AcademySoftwareFoundation/OpenRV/blob/d96b2a8c93525da39bb2dc721690f214d3ea9181/src/lib/ip/OCIONodes/OCIOIPNode.cpp#L231
        os.environ["OCIO"] = ocio_config_path.as_posix()

    logger.debug(f"Loading OCIO config: {ocio_config_path.as_posix()}")
    config_module = OCIO.Config()
    config = config_module.CreateFromFile(str(ocio_config_path))

    # validate configuration
    for _field in ["working_space", "exr_colorspace"]:
        colorspace = getattr(autoloader_config.color, _field)
        if not (validated_colorspace := config.parseColorSpaceFromString(colorspace)):
            raise Exception(
                f"Configuration error: Could not find color space: {colorspace}"
            )
        setattr(autoloader_config.color, _field, validated_colorspace)

    return config
