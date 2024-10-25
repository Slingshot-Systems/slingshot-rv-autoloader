# Copyright (C) 2024 Slingshot Systems Inc.
# SPDX-License-Identifier: Apache-2.0


import logging
from dataclasses import dataclass
from pathlib import Path
from queue import Queue

from config import get_config_path, read_settings
from rv import commands, extra_commands, rvtypes
from rv_schemas.event import Event
from rv_schemas.menu import MenuItem

logging.basicConfig()
logger = logging.getLogger("SlingshotAutoLoader")
logger.setLevel(logging.DEBUG)
# todo:
# - bind to the 'incoming-source-path' event and add additional media representations for plates anv v000s (also .mov and frames?)
# - bind to the 'incoming-source-path' event and load luts and CDLs
# add debug setting to menu and set the log level based on it

SETTINGS_NAME = "SLINGSHOT_AUTO_LOADER"


@dataclass
class PendingMediaRep:
    sourceNode: str
    mediaRepName: str
    mediaRepPathsAndOptions: list[str]
    tag: str | None = None


class SlingshotAutoLoaderMode(rvtypes.MinorMode):
    _enabled: bool = True
    _autoload_queue: Queue[PendingMediaRep] = Queue()

    def __init__(self):
        super().__init__()

        self.config = read_settings()

        self._enabled = commands.readSettings(SETTINGS_NAME, "enabled", self._enabled)

        init_bindings = [
            (
                "source-group-complete",
                self.auto_load_plates,
                "Auto load plates and v000s",
            ),
            ("source-media-set", self.on_source_media_set, "On source media set"),
            (
                "incoming-source-path",
                self.on_incoming_source_path,
                "On incoming source path",
            ),
            (
                "after-progressive-loading",
                self.after_progressive_loading,
                "Auto load additional media representations",
            ),
        ]

        self.init(
            "rv-auto-loader",
            init_bindings,
            None,
            menu=self.give_menu(),
            # sortKey="multiple_source_media_rep",
            ordering=30,  # run our actions after native MultipleSourceMediaRepMode package
        )

    def give_menu(self):
        return [
            (
                "Slingshot Auto Loader",
                [
                    (
                        "Auto Load",
                        [
                            MenuItem(
                                label=f"Plate MOVs: {self.config.plates.plate_mov_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"Plate Frames: {self.config.plates.plate_frames_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"v000 MOVs: {self.config.plates.v000_mov_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"v000 Frames: {self.config.plates.v000_frames_path}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                            MenuItem(
                                label=f"To configure these, edit {get_config_path().name}",
                                stateHook=lambda: commands.DisabledMenuState,
                            ).tuple(),
                        ],
                    ),
                    MenuItem("_").tuple(),
                    MenuItem(
                        label="Enable",
                        actionHook=self.toggle_enabled,
                        stateHook=self.is_enabled,
                    ).tuple(),
                ],
            )
        ]

    def is_enabled(self):
        print(f"is_enabled: {self._enabled} {str(type(self._enabled)).strip('><')}")
        if self._enabled:
            print("is_enabled")
            return commands.CheckedMenuState
        else:
            print("is_disabled")
            return commands.UncheckedMenuState

    def toggle_enabled(self, event: "Event"):
        self._enabled = not self._enabled
        print(f"toggle_enabled -> {self._enabled}")
        commands.writeSettings(SETTINGS_NAME, "enabled", self._enabled)

    def auto_load_plates(self, event: "Event"):
        logger.debug(f"auto_load_plates: {event.contents()}")
        #  The contents of the "source-group-complete" looks like "group nodename;;action_type"
        group, action_type = event.contents().split(";;")

        event.reject()

        if not self._enabled:
            logger.debug("Auto loader disabled")
            return

        file_source = extra_commands.nodesInGroupOfType(group, "RVFileSource")[0]
        source_groups = extra_commands.nodesInGroupOfType(group, "RVSourceGroup")
        switch_nodes = extra_commands.nodesInGroupOfType(group, "RVSwitch")
        print("switch_node", switch_nodes)

        source_path = Path(
            commands.getStringProperty(f"{file_source}.media.movie", 0, 1000)[0]
        )

        try:
            print("INFO!!", commands.sourceMediaInfo(file_source, str(source_path)))
        except Exception:
            pass

        media_reps = commands.sourceMediaReps(file_source)

        _media_rep_name_lookup = {
            "plate_mov_path": "Plate",
            "plate_frames_path": "Plate Frames",
            "v000_mov_path": "v000",
            "v000_frames_path": "v000 Frames",
        }

        for _plate in self.config.plates.__dataclass_fields__:
            media_rep_name = _media_rep_name_lookup[_plate]
            if media_rep_name in media_reps:
                continue

            new_source_relative_path: str = getattr(self.config.plates, _plate)
            if not new_source_relative_path:
                logger.debug(f"{new_source_relative_path} not configured")
                continue

            try:
                new_source_file = next(
                    source_path.parent.glob(new_source_relative_path)
                ).resolve()
            except StopIteration:
                logger.warning(
                    f"Can't autoload: {_plate} {source_path.parent}/{new_source_relative_path} does not exist"
                )
                continue

            # adding new media representations here interferes with the Flow Production Tracking Mode
            # specifically in shotgrid_mode.mu method: afterProgressiveLoading (void; Event event)
            # ERROR: after progressive loading, number of new sources (%s) != infos (%s)"
            # an error is thrown and the Flow sources don't get updated with infro from the Flow fields
            # so we queue up our changes here and then run them all after progressive loading is done.

            logger.debug(f"Queueing autoload {media_rep_name} {new_source_file}")
            self._autoload_queue.put(
                PendingMediaRep(
                    file_source, media_rep_name, [str(new_source_file)], "autoload"
                )
            )

    def on_source_media_set(self, event: "Event"):
        logger.debug(f"on_source_media_set: {event.contents()}")

    def on_incoming_source_path(self, event: "Event"):
        logger.debug(f"on_incoming_source_path: {event.contents()}")
        #  The contents of the "source-group-complete" looks like "group nodename;;action_type"
        infilename, tag = event.contents().split(";;")

    def after_progressive_loading(self, event: "Event"):
        logger.debug(f"after_progressive_loading: {event.contents()}")

        while not self._autoload_queue.empty():
            rep = self._autoload_queue.get_nowait()
            logger.info(f"Autoloading {rep.mediaRepName} {rep.mediaRepPathsAndOptions}")
            try:
                commands.addSourceMediaRep(
                    rep.sourceNode,
                    rep.mediaRepName,
                    rep.mediaRepPathsAndOptions,
                    rep.tag,
                )
            except Exception:
                # source media representation name already exists, probably
                # Exception: Exception thrown while calling commands.addSourceMediaRep, ERROR: Source media representation name already exists:
                continue

        event.reject()


def createMode():
    return SlingshotAutoLoaderMode()
