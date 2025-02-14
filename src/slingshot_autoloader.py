# Copyright (C) 2024 Slingshot Systems Inc.
# SPDX-License-Identifier: Apache-2.0


import logging
import re
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from string import Template
from typing import TYPE_CHECKING, Callable

import PyOpenColorIO as OCIO

from rv import commands, extra_commands, rvtypes
from rv_menu_schema import MenuItem
from slingshot_autoloader_config import get_config_path, get_ocio_config, read_settings

if TYPE_CHECKING:
    from rv_schemas.event import Event
    from rv_schemas.ocio import OCIOProperties

logging.basicConfig()
logger = logging.getLogger("SlingshotAutoLoader")
logger.setLevel(logging.INFO)


@dataclass
class PendingMediaRep:
    sourceNode: str
    mediaRepName: str
    mediaRepPath: Path
    tag: str | None = None


@dataclass
class Settings:
    RV_SETTINGS_GROUP = "SLINGSHOT_AUTO_LOADER"
    load_plates_enabled: bool = True
    load_other_enabled: bool = True
    load_luts_enabled: bool = True
    debug: bool = False


class SlingshotAutoLoaderMode(rvtypes.MinorMode):
    _settings: Settings = Settings()
    _autoload_queue: Queue[PendingMediaRep] = Queue()
    _delete_node: str | None = None

    def __init__(self):
        super().__init__()

        self.config = read_settings()

        OCIO.SetCurrentConfig(get_ocio_config(self.config))

        self._settings.load_plates_enabled = commands.readSettings(
            self._settings.RV_SETTINGS_GROUP,
            "load_plates_enabled",
            self._settings.load_plates_enabled,
        )
        self._settings.load_other_enabled = commands.readSettings(
            self._settings.RV_SETTINGS_GROUP,
            "load_other_enabled",
            self._settings.load_other_enabled,
        )
        self._settings.load_luts_enabled = commands.readSettings(
            self._settings.RV_SETTINGS_GROUP,
            "load_luts_enabled",
            self._settings.load_luts_enabled,
        )
        self._settings.debug = commands.readSettings(
            self._settings.RV_SETTINGS_GROUP, "debug", self._settings.debug
        )

        logger.setLevel(logging.DEBUG if self._settings.debug else logging.INFO)

        init_bindings = [
            (
                "source-group-complete",
                self.on_source_group_complete,
                "Auto detect plates and v000s",
            ),
            (
                "after-progressive-loading",
                self.after_progressive_loading,
                "Load additional v000/plate media representations",
            ),
        ]

        self.init(
            "rv-auto-loader",
            init_bindings,
            None,
            menu=self.give_menu(),
            # sortKey="multiple_source_media_rep",
            ordering=30,  # run our actions last, after Flow Production Tracking package
        )

    def give_menu(self):
        return [
            (
                "Slingshot Auto Loader",
                [
                    (
                        "Current Configuration",
                        [
                            MenuItem(
                                "Autoload Plates",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Plate MOVs: {self.config.plates.plate_mov_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Plate Frames: {self.config.plates.plate_frames_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Plates first frame is: {self.config.plates.plate_first_frame_in_file}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Plates cut in on: {self.config.plates.plate_cut_in_frame}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem("_").tuple(),
                            MenuItem(
                                "Autoload Other Media",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                        ]
                        + [
                            MenuItem(
                                label=f"    {media_rep.replace('_', ' ')}: {path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple()
                            for media_rep, path in self.config.other.items()
                        ]
                        + [
                            MenuItem("_").tuple(),
                            MenuItem(
                                "Autoload LUT/CDLs",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    MOV Colorspace: {self.config.color.mov_colorspace}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    EXR Colorspace: {self.config.color.exr_colorspace}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Working Colorspace: {self.config.color.working_space}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Look CDL: {self.config.color.look_cdl}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    Look LUT: {self.config.color.look_lut}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem("_").tuple(),
                            MenuItem(
                                label=f"To configure these, edit {get_config_path().name}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                        ],
                    ),
                    MenuItem("_").tuple(),
                    MenuItem(
                        label="Autoload Plates",
                        actionHook=self.toggle_setting("load_plates_enabled"),
                        stateHook=self.is_enabled("load_plates_enabled"),
                    ).tuple(),
                    MenuItem(
                        label="Autoload Other Media",
                        actionHook=self.toggle_setting("load_other_enabled"),
                        stateHook=self.is_enabled("load_other_enabled"),
                    ).tuple(),
                    MenuItem(
                        label="Autoload LUTs/CDLs",
                        actionHook=self.toggle_setting("load_luts_enabled"),
                        stateHook=self.is_enabled("load_luts_enabled"),
                    ).tuple(),
                    MenuItem(
                        label="Debug Logging",
                        actionHook=self.toggle_setting("debug"),
                        stateHook=self.is_enabled("debug"),
                    ).tuple(),
                ],
            )
        ]

    def is_enabled(self, settings_name: str) -> Callable[[], int]:
        def _is_enabled() -> int:
            return (
                commands.CheckedMenuState
                if getattr(self._settings, settings_name)
                else commands.UncheckedMenuState
            )

        return _is_enabled

    def toggle_setting(self, settings_name: str) -> Callable[..., None]:
        def _toggle(event: "Event"):
            new_setting = not getattr(self._settings, settings_name)
            setattr(self._settings, settings_name, new_setting)
            commands.writeSettings(
                self._settings.RV_SETTINGS_GROUP, settings_name, new_setting
            )

            if settings_name == "debug":
                logger.setLevel(logging.DEBUG if new_setting else logging.INFO)

        return _toggle

    def _find_file(self, source_path: Path, search_path: str) -> Path | None:
        if matches := re.search(
            self.config.main.version_regex, source_path.name, re.IGNORECASE
        ):
            search_path = Template(search_path).safe_substitute(**matches.groupdict())

        if not (file_path := Path(search_path)).is_absolute():
            try:
                file_path = next(source_path.parent.glob(search_path)).resolve()
            except StopIteration:
                logger.warning(f"Can't find file: {source_path.parent}/{search_path}")
                return

        if not file_path.is_file():
            logger.warning(f"Can't load file: {file_path} is not a file")
            return

        return file_path

    def on_source_group_complete(self, event: "Event"):
        logger.debug(f"auto_load_plates: {event.contents()}")
        #  The contents of the "source-group-complete" looks like "group nodename;;action_type"
        group, action_type = event.contents().split(";;")

        event.reject()

        self.autoload_media(group)
        self.autoload_color(group)

    def autoload_media(self, source_group: str):
        if (
            not self._settings.load_plates_enabled
            and not self._settings.load_other_enabled
        ):
            logger.debug("Plate and other auto loaders disabled")
            return

        file_source = extra_commands.nodesInGroupOfType(source_group, "RVFileSource")[0]
        source_path = Path(
            commands.getStringProperty(f"{file_source}.media.movie", 0, 1000)[0]
        )
        if (media_reps := commands.sourceMediaReps(file_source)) != [""]:
            self._enqueue_plate_autoloads(file_source, source_path, media_reps)
        else:
            # no media reps, we need to add our default
            return self._add_default_media_rep(source_group, file_source, source_path)

    def _enqueue_plate_autoloads(
        self, file_source: str, source_path: Path, media_reps: list[str]
    ):
        if self._settings.load_plates_enabled:
            _media_rep_name_lookup = {
                "plate_mov_path": "Plate",
                "plate_frames_path": "Plate Frames",
            }

            for _plate, media_rep_name in _media_rep_name_lookup.items():
                if media_rep_name in media_reps:
                    continue

                new_source_relative_path: str = getattr(self.config.plates, _plate)
                if not new_source_relative_path:
                    logger.debug(f"{_plate} not configured")
                    continue

                new_source_file = self._find_file(source_path, new_source_relative_path)
                if not new_source_file:
                    logger.warning(f"Can't autoload: {_plate}")
                    continue

                # adding new media representations here interferes with the Flow Production Tracking Mode
                # specifically in shotgrid_mode.mu method: afterProgressiveLoading (void; Event event)
                #      > ERROR: after progressive loading, number of new sources (%s) != infos (%s)"
                # an error is thrown and the Flow sources don't get updated with info from the Flow fields
                # so we queue up our changes and then run them all after progressive loading is done.
                logger.debug(f"Queueing autoload {media_rep_name} {new_source_file}")
                self._autoload_queue.put(
                    PendingMediaRep(
                        file_source, media_rep_name, new_source_file, "autoload"
                    )
                )
        if self._settings.load_other_enabled:
            for name, path in self.config.other.items():
                media_rep_name = name.replace("_", " ")
                if media_rep_name in media_reps:
                    continue

                new_source_file = self._find_file(source_path, path)
                if not new_source_file:
                    logger.warning(f"Can't autoload: {name}")
                    continue

                logger.debug(f"Queueing autoload {media_rep_name} {new_source_file}")
                self._autoload_queue.put(
                    PendingMediaRep(
                        file_source, media_rep_name, new_source_file, "autoload"
                    )
                )

    def _add_default_media_rep(
        self, source_group: str, file_source: str, source_path: Path
    ):
        logger.debug("Adding 'Source' media representation")
        rep_node = commands.addSourceMediaRep(file_source, "Source", [str(source_path)])
        commands.setActiveSourceMediaRep(file_source, "Source")

        # flag for deletion in after_progressive_loading
        self._delete_node = source_group

        # rename switch node in UI with filename
        switch_node = commands.sourceMediaRepSwitchNode(rep_node)
        if switch_node != "":
            logger.debug(f"configuring switch node: {switch_node} {source_path.name}")
            extra_commands.setUIName(commands.nodeGroup(switch_node), source_path.name)
            # if self.config.plates.plate_offset:
            #     commands.setIntProperty(f"{switch_node}.mode.alignStartFrames", [1])
        return

    def autoload_color(self, source_group: str):
        if not self._settings.load_luts_enabled:
            logger.debug("LUT auto loader disabled")
            return

        file_source = extra_commands.nodesInGroupOfType(source_group, "RVFileSource")[0]
        source_path = Path(
            commands.getStringProperty(f"{file_source}.media.movie", 0, 1000)[0]
        )

        if source_path.suffix.lower() in {
            ".mov",
        }:
            self._setup_mov_linearize_node(source_group)
        elif source_path.suffix.lower() in {".dpx", ".exr"}:
            self._setup_exr_linearize_node(source_group)
            self._add_look_luts(source_group, source_path)

    def _setup_mov_linearize_node(self, source_group: str):
        """Sets Color -> File Nonlinear to Linear Conversion"""
        linPipeNode = extra_commands.nodesInGroupOfType(
            source_group, "RVLinearizePipelineGroup"
        )[0]
        linNode = extra_commands.nodesInGroupOfType(linPipeNode, "RVLinearize")[0]

        sRGB = 0
        logT = 0
        r709 = 0

        transfer_function = self.config.color.mov_colorspace

        if transfer_function == "sRGB":
            sRGB = 1
        elif transfer_function == "Rec709":
            r709 = 1
        elif transfer_function != "Linear":
            raise ValueError(f"Unknown transfer function: {transfer_function}")

        commands.setIntProperty(f"{linNode}.color.sRGB2linear", [sRGB], True)
        commands.setIntProperty(f"{linNode}.color.logtype", [logT], True)
        commands.setIntProperty(f"{linNode}.color.Rec709ToLinear", [r709], True)

    def _setup_exr_linearize_node(self, source_group: str):
        file_pipe = extra_commands.nodesInGroupOfType(
            source_group, "RVLinearizePipelineGroup"
        )[0]
        logger.debug(
            f"Adding Linearize EXR OCIO node - in colorspace: {self.config.color.exr_colorspace},"
            f" out colorspace: {self.config.color.working_space}",
        )
        commands.setStringProperty(f"{file_pipe}.pipeline.nodes", ["OCIOFile"], True)
        ocio_node = extra_commands.nodesInGroupOfType(file_pipe, "OCIOFile")[0]
        applyOCIOProps(
            ocio_node,
            {
                "ocio.function": "color",
                "ocio.inColorSpace": self.config.color.exr_colorspace,
                "ocio_color.outColorSpace": self.config.color.working_space,
            },
        )

    def _add_look_luts(self, source_group: str, source_path: Path):
        look_pipe = extra_commands.nodesInGroupOfType(
            source_group, "RVLookPipelineGroup"
        )[0]

        look_pipeline = []

        if self.config.color.look_cdl:
            look_pipeline.append("RVColor")

        if self.config.color.look_lut:
            look_pipeline += ["RVLookLUT", "Rec709ToLinear"]

        commands.setStringProperty(f"{look_pipe}.pipeline.nodes", look_pipeline, True)

        self._add_look_cdl(source_path, look_pipe)
        self._add_look_lut(source_path, look_pipe)

        # print a debug summary
        _look_pipe_nodes = commands.nodesInGroup(look_pipe)
        _look_pipe_node_summary = [
            f"{commands.nodeType(node)}: {node}" for node in _look_pipe_nodes
        ]
        _look_pipe_summary = ",\n".join(_look_pipe_node_summary)
        logger.debug(f"{look_pipe}: {_look_pipe_summary}")

    def _add_look_cdl(self, source_path: Path, look_pipe: str):
        if not self.config.color.look_cdl:
            return

        if not (cdl_path := self._find_file(source_path, self.config.color.look_cdl)):
            logger.warning("Can't load look CDL")
            return

        color_node = extra_commands.nodesInGroupOfType(look_pipe, "RVColor")[0]
        logger.info(f"Loading look CDL {cdl_path}")
        commands.readCDL(str(cdl_path), color_node, True)

    def _add_look_lut(self, source_path: Path, look_pipe: str):
        if not self.config.color.look_lut:
            return

        if not (lut_path := self._find_file(source_path, self.config.color.look_lut)):
            logger.warning("Can't load look LUT")
            return

        look_node = extra_commands.nodesInGroupOfType(look_pipe, "RVLookLUT")[0]
        logger.info(f"Loading look LUT: {lut_path}")
        commands.readLUT(str(lut_path), look_node, True)

    def after_progressive_loading(self, event: "Event"):
        logger.debug(f"after_progressive_loading: {event.contents()}")

        while not self._autoload_queue.empty():
            rep = self._autoload_queue.get_nowait()
            logger.info(f"Autoloading {rep.mediaRepName} {rep.mediaRepPath}")
            try:
                new_rep = commands.addSourceMediaRep(
                    rep.sourceNode,
                    rep.mediaRepName,
                    [str(rep.mediaRepPath)],
                    rep.tag,
                )
            except Exception:
                # source media representation name already exists, probably
                # Exception: Exception thrown while calling commands.addSourceMediaRep, ERROR: Source media representation name already exists:
                continue

            extra_commands.setUIName(
                commands.nodeGroup(new_rep),
                f"{rep.mediaRepPath.name} ({rep.mediaRepName})",
            )

            if rep.mediaRepName.startswith("Plate"):
                logger.debug(
                    f"Setting {new_rep} plate cut.in: {self.config.plates.plate_cut_in_frame} rangeStart: {self.config.plates.plate_first_frame_in_file}"
                )
                if self.config.plates.plate_cut_in_frame:
                    commands.setIntProperty(
                        f"{new_rep}.cut.in", [self.config.plates.plate_cut_in_frame]
                    )

                if self.config.plates.plate_first_frame_in_file:
                    if not commands.propertyExists(f"{new_rep}.group.rangeStart"):
                        commands.newProperty(
                            f"{new_rep}.group.rangeStart", commands.IntType, 1
                        )
                    commands.setIntProperty(
                        f"{new_rep}.group.rangeStart",
                        [self.config.plates.plate_first_frame_in_file],
                        True,
                    )

        if self._delete_node:
            logger.debug(f"Deleting {self._delete_node}")
            commands.deleteNode(self._delete_node)
            self._delete_node = None

        event.reject()


def createMode():
    return SlingshotAutoLoaderMode()


def applyOCIOProps(node: str, properties: "OCIOProperties"):
    for prop, value in properties.items():
        if isinstance(value, str):
            commands.setStringProperty(f"{node}.{prop}", [value], True)
        elif isinstance(value, int):
            commands.setIntProperty(f"{node}.{prop}", [value], True)
        elif isinstance(value, float):
            commands.setFloatProperty(f"{node}.{prop}", [value], True)
        else:
            raise ValueError(
                f"Cannot set property {prop} with value of type {type(value)}"
            )
