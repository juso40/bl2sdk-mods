from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING, Any, cast

from mods_base import ENGINE, build_mod, hook, options
from unrealsdk import logging, unreal
from unrealsdk.hooks import Type

from maploader import loader, maps

if TYPE_CHECKING:
    from common import WillowGameEngine, WillowPlayerController

__all__ = ["mod"]

__version__: str
__version_info__: tuple[int, ...]

map_definitions: dict[str, maps.MapDefinition] = {definition.name: definition for definition in maps.discover_maps()}

threaded_loading = options.BoolOption(
    identifier="Threaded Loading",
    value=False,
    description=(
        "Load map changes asynchronously after travelling."
        " This shortens loading screens but can cause objects to pop in."
    ),
)

def _map_option_changed(option: options.BoolOption, value: bool) -> None:
    if value:
        logging.info(f"Preloading Kept Alive Objects for map '{option.identifier}'")
        loader.keep_alive_objects(option.identifier)
    else:
        logging.info(f"Unloading Kept Alive Objects for map '{option.identifier}'")
        loader.unload_kept_alive_objects(option.identifier)

map_options: dict[str, options.BoolOption] = {
    name: options.BoolOption(
        identifier=name,
        value=True,
        on_change=_map_option_changed,
        description=(
            f"Modifies: {', '.join(definition.modified_maps) if definition.modified_maps else 'Unknown maps'}"
        ),
    )
    for name, definition in map_definitions.items()
}

loader_threads: list[Thread] = []



def _current_map_name() -> str:
    return cast("WillowGameEngine", ENGINE).GetCurrentWorldInfo().GetStreamingPersistentMapName().lower()


def _load_map(map_name: str, current_map: str) -> None:
    try:
        loader.load_map(map_name, current_map)
    except Exception:  # noqa: BLE001
        logging.error(f"Failed to load map '{map_name}' for '{current_map}'")


def _join_threads() -> None:
    for thread in loader_threads:
        thread.join()
    loader_threads.clear()
    loader_tick.disable()


def _on_disable() -> None:
    _join_threads()
    loader.unload_map()


@hook("WillowGame.WillowPlayerController:WillowClientDisableLoadingMovie", hook_type=Type.POST)
def on_end_load(
    obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    pc = cast("WillowPlayerController", obj)
    if not pc.IsLocalPlayerController():
        return

    current_map = _current_map_name()
    for name, option in map_options.items():
        if not option.value:
            continue

        definition = map_definitions.get(name)
        if definition is None or current_map not in definition.modified_maps:
            continue

        if threaded_loading.value:
            thread = Thread(target=_load_map, args=(name, current_map), daemon=True)
            loader_threads.append(thread)
            thread.start()
            loader_tick.enable()
        else:
            _load_map(name, current_map)


@hook("WillowGame.WillowPlayerController:WillowClientShowLoadingMovie", hook_type=Type.POST)
def on_start_load(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    pc = cast("WillowPlayerController", obj)
    if not pc.IsLocalPlayerController():
        return

    _join_threads()
    if args.MovieName:
        loader.unload_map()


@hook("WillowGame.WillowGameViewportClient:Tick", hook_type=Type.POST_UNCONDITIONAL)
def loader_tick(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    loader_threads[:] = [thread for thread in loader_threads if thread.is_alive()]
    if not loader_threads:
        loader_tick.disable()


loader_tick.disable()


mod = build_mod(
    options=[threaded_loading, *map_options.values()],
    hooks=[on_start_load, on_end_load, loader_tick],
    on_disable=_on_disable,
)
mod.load_settings()
