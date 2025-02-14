import logging
import os
from configparser import ConfigParser
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path

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
    mov_colorspace: str = "Rec709"
    exr_colorspace: str = "ACES2065-1"
    working_space: str = "ACEScc"
    look_cdl: str | None = None
    look_lut: str | None = None


@dataclass(frozen=True)
class AutoloaderConfig:
    main: AutoloadMainConfig = AutoloadMainConfig()
    plates: AutoloadPlatesConfig = AutoloadPlatesConfig()
    other: dict[str, str] = field(default_factory=dict)
    color: AutoloadColorConfig = AutoloadColorConfig()


def read_settings() -> AutoloaderConfig:
    _config = get_or_create_default_config()

    return AutoloaderConfig(
        main=AutoloadMainConfig(
            version_regex=_config["main"].get("version_regex")
            or AutoloadMainConfig.__dataclass_fields__["version_regex"].default
        )
        if _config.has_section("main")
        else AutoloadMainConfig(),
        plates=AutoloadPlatesConfig(
            plate_mov_path=_config["plates"].get("plate_mov_path"),
            plate_frames_path=_config["plates"].get("plate_frames_path"),
            plate_first_frame_in_file=int(
                _config["plates"]["plate_first_frame_in_file"]
            )
            if _config["plates"].get("plate_first_frame_in_file")
            else None,
            plate_cut_in_frame=int(_config["plates"]["plate_cut_in_frame"])
            if _config["plates"].get("plate_cut_in_frame")
            else None,
        )
        if _config.has_section("plates")
        else AutoloadPlatesConfig(),
        other={k: v for k, v in _config["other"].items() if v}
        if _config.has_section("other")
        else {},
        color=AutoloadColorConfig(
            mov_colorspace=_config["color"].get("mov_colorspace")
            or AutoloadColorConfig.__dataclass_fields__["mov_colorspace"].default,
            exr_colorspace=_config["color"].get("exr_colorspace")
            or AutoloadColorConfig.__dataclass_fields__["exr_colorspace"].default,
            working_space=_config["color"].get("working_space")
            or AutoloadColorConfig.__dataclass_fields__["working_space"].default,
            look_cdl=_config["color"].get("look_cdl"),
            look_lut=_config["color"].get("look_lut"),
        )
        if _config.has_section("color")
        else AutoloadColorConfig(),
    )


def get_config_path() -> Path:
    """Gets the path to the config file in the user's home directory."""

    return Path.home() / ".slingshot_rv_autoloader.cfg"


def get_or_create_default_config() -> ConfigParser:
    """Reads the config file, and creates a default if it doesn't exist."""

    config_file = get_config_path()
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str  # don't lowercase keys # type: ignore
    if not config_file.exists():
        for field, value in asdict(AutoloaderConfig()).items():
            if is_dataclass(value) and not isinstance(value, type):
                _value = asdict(value)
            elif isinstance(value, dict):
                _value = value
            else:
                _value = {}

            config[field] = _value

        with open(config_file, "w") as f:
            config.write(f)

        return config

    config.read(config_file)
    return config


def get_ocio_config(autoloader_config: AutoloaderConfig) -> OCIO.Config:
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
