from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AutoloadPlatesConfig:
    plate_mov_path: str | None = None
    plate_frames_path: str | None = None
    plate_cut_in_frame: int | None = None
    plate_first_frame_in_file: int | None = None
    v000_mov_path: str | None = None
    v000_frames_path: str | None = None


@dataclass(frozen=True)
class AutoloadColorConfig:
    file_lut: str | None = None
    look_cdl: str | None = None
    look_lut: str | None = None


@dataclass(frozen=True)
class AutoloaderConfig:
    plates: AutoloadPlatesConfig = AutoloadPlatesConfig()
    color: AutoloadColorConfig = AutoloadColorConfig()


def read_settings() -> AutoloaderConfig:
    _config = get_or_create_default_config()

    return AutoloaderConfig(
        plates=AutoloadPlatesConfig(
            plate_mov_path=_config["plates"].get("plate_mov_path"),
            plate_frames_path=_config["plates"].get("plate_frames_path"),
            v000_mov_path=_config["plates"].get("v000_mov_path"),
            v000_frames_path=_config["plates"].get("v000_frames_path"),
            plate_first_frame_in_file=_config["plates"].getint(
                "plate_first_frame_in_file"
            ),
            plate_cut_in_frame=_config["plates"].getint("plate_cut_in_frame"),
        )
        if _config.has_section("plates")
        else AutoloadPlatesConfig(),
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
    if not config_file.exists():
        for k, v in AutoloaderConfig().__dict__.items():
            config[k] = v.__dict__

        with open(config_file, "w") as f:
            config.write(f)

        return config

    config.read(config_file)
    return config
