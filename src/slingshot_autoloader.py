# Copyright (C) 2024 Slingshot Systems Inc.
# SPDX-License-Identifier: Apache-2.0


import logging
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Callable

from rv import commands, extra_commands, rvtypes
from rv_menu_schema import MenuItem
from slingshot_autoloader_config import get_config_path, read_settings

if TYPE_CHECKING:
    from rv_schemas.event import Event

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
    load_luts_enabled: bool = True
    debug: bool = False


class SlingshotAutoLoaderMode(rvtypes.MinorMode):
    _settings: Settings = Settings()
    _autoload_queue: Queue[PendingMediaRep] = Queue()
    _delete_node: str | None = None

    def __init__(self):
        super().__init__()

        self.config = read_settings()

        self._settings.load_plates_enabled = commands.readSettings(
            self._settings.RV_SETTINGS_GROUP,
            "load_plates_enabled",
            self._settings.load_plates_enabled,
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
                                "LUT/CDLs",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    File LUT: {self.config.color.file_lut}",
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
                                "Plates/v000s",
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
                                label=f"    v000 MOVs: {self.config.plates.v000_mov_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"    v000 Frames: {self.config.plates.v000_frames_path}",
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
                                label=f"To configure these, edit {get_config_path().name}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                        ],
                    ),
                    MenuItem("_").tuple(),
                    MenuItem(
                        label="Autoload Plates/v000s",
                        actionHook=self.toggle_setting("load_plates_enabled"),
                        stateHook=self.is_enabled("load_plates_enabled"),
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

        self.autoload_plates(group)
        self.autoload_color(group)

    def autoload_plates(self, source_group: str):
        if not self._settings.load_plates_enabled:
            logger.debug("Plate auto loader disabled")
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
        _media_rep_name_lookup = {
            "plate_mov_path": "Plate",
            "plate_frames_path": "Plate Frames",
            "v000_mov_path": "v000",
            "v000_frames_path": "v000 Frames",
        }

        for _plate, media_rep_name in _media_rep_name_lookup.items():
            if media_rep_name in media_reps:
                continue

            new_source_relative_path: str = getattr(self.config.plates, _plate)
            if not new_source_relative_path:
                logger.debug(f"{new_source_relative_path} not configured")
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

        if source_path.suffix.lower() not in (".dpx", ".exr"):
            return

        self._add_file_lut(source_group, source_path)
        self._add_look_luts(source_group, source_path)

    def _add_file_lut(self, source_group: str, source_path: Path):
        if not self.config.color.file_lut:
            return

        # decide if it's a path or a node name
        if any(v in self.config.color.file_lut for v in (".", "*", "\\", "/")):
            # it's a LUT path
            if not (
                lut_path := self._find_file(source_path, self.config.color.file_lut)
            ):
                logger.warning("Can't load file LUT")
                return

            logger.info(f"Loading File LUT {lut_path}")
            commands.readLUT(str(lut_path), "#RVLinearize", True)

        else:
            # it's a node name
            file_pipe = extra_commands.nodesInGroupOfType(
                source_group, "RVLinearizePipelineGroup"
            )[0]
            # add node to file pipeline
            logger.info(
                f"Adding {self.config.color.file_lut} Node to Linearize Pipeline"
            )
            commands.setStringProperty(
                f"{file_pipe}.pipeline.nodes",
                ["RVLinearize", self.config.color.file_lut],
                True,
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
        logger.debug(f"{look_pipe}: {','.join(_look_pipe_node_summary)}")

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

        # elif (nodeType == "RVLookPipelineGroup"):
        #     # If our config has a Look named shot_specific_look and uses the
        #     # environment/context variable "$SHOT" to locate any required
        #     # files on disk, then this is what that would likely look like
        #     result = [
        #         {"nodeType"   : "OCIOLook",
        #         "context"    : {},
        #         "properties" : {
        #             "ocio.function"     : "look",
        #             "ocio.inColorSpace" : OCIO.Constants.ROLE_SCENE_LINEAR,
        #             "ocio_look.look"    : "role_color_my_look"}}]

        # linPipeNode = extra_commands.nodesInGroupOfType(
        #     source_group, "RVLinearizePipelineGroup"
        # )[0]
        # linNode = extra_commands.nodesInGroupOfType(linPipeNode, "RVLinearize")[0]
        # ICCNode = extra_commands.nodesInGroupOfType(
        #     linPipeNode, "ICCLinearizeTransform"
        # )[0]
        # lensNode = extra_commands.nodesInGroupOfType(linPipeNode, "RVLensWarp")[0]
        # fmtNode = extra_commands.nodesInGroupOfType(source_group, "RVFormat")[0]
        # tformNode = extra_commands.nodesInGroupOfType(source_group, "RVTransform2D")[0]
        # lookPipeNode = extra_commands.nodesInGroupOfType(
        #     source_group, "RVLookPipelineGroup"
        # )[0]
        # lookNode = extra_commands.nodesInGroupOfType(lookPipeNode, "RVLookLUT")[0]
        # typeName = commands.nodeType(file_source)

        # mInfo = commands.sourceMediaInfo(file_source, None)
        # try:
        #     srcAttrs = commands.sourceAttributes(file_source, source_path.name)
        #     srcData = commands.sourceDataAttributes(file_source, source_path.name)
        # except Exception:
        #     return

        # if srcAttrs is None:
        #     print(
        #         f"ERROR: SourceSetup: source {file_source}/{source_path.name} has no attributes"
        #     )
        #     return

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
