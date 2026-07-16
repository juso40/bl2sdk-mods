from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import unrealsdk
from unrealsdk import find_object, logging

from maploader import placeablehelper

MAPS_DIR = Path(__file__).parent / "Maps"


def load_map(map_name: str, current_map: str) -> None:
    """Load a map for a specific level."""
    map_data = _load_map_file(map_name)
    if not map_data:
        return

    level_data = {key.lower(): value for key, value in map_data.items()}.get(current_map)
    if not level_data:
        return

    placeablehelper.load_map(level_data)


def unload_map() -> None:
    placeablehelper.unload_map()


def keep_alive_objects(map_name: str) -> None:
    """Load the objects of a map by its file name without extension."""
    map_data = _load_map_file(map_name)
    if not map_data:
        return

    to_load = map_data.get("LoadedObjects", {})
    for package, objects in to_load.items():
        if load_package(package):
            for obj_path in objects:
                _keep_alive(obj_path)


def unload_kept_alive_objects(map_name: str) -> None:
    map_data = _load_map_file(map_name)
    if not map_data:
        return

    to_load = map_data.get("LoadedObjects", {})
    for _package, objects in to_load.items():
        # ignore package, we assume the objects are already loaded
        for obj_path in objects:
            _keep_alive(obj_path, True)


def load_package(name: str) -> bool:
    """Load an Unreal package by name."""
    try:
        unrealsdk.load_package(name)
        logging.info(f"Loaded package: {name}")
        return True
    except Exception as e:  # noqa: BLE001
        logging.error(f"Failed to load package '{name}': {e}")
        return False


def _keep_alive(path_name: str, undo: bool = False) -> bool:
    try:
        obj = find_object("Object", path_name)
    except Exception as e:  # noqa: BLE001
        logging.error(f"Error finding object '{path_name}': {e}")
        return False
    if undo:
        obj.ObjectFlags &= ~0x4000
    else:
        obj.ObjectFlags |= 0x4000
    return True


def _load_map_file(map_name: str) -> dict[str, Any] | None:
    path = MAPS_DIR / f"{map_name}.json"
    try:
        with path.open(encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError:
        logging.warning(f"Map '{map_name}' does not exist at '{path}'")
    except Exception:  # noqa: BLE001
        logging.error(f"Failed to load map '{map_name}' from '{path}'")
    return None
