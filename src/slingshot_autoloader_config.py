from configparser import ConfigParser
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path


@dataclass(frozen=True)
class AutoloadMainConfig:
    version_regex: str = r"_(?P<version>v\d+)"


@dataclass(frozen=True)
class AutoloadPlatesConfig:
    plate_mov_path: str | None = None
    plate_frames_path: str | None = None
    plate_cut_in_frame: int | None = None
    plate_first_frame_in_file: int | None = None


@dataclass(frozen=True)
class AutoloadColorConfig:
    file_lut: str | None = None
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
            file_lut=_config["color"].get("file_lut"),
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
