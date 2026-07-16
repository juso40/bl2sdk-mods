from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from unrealsdk import logging

MAPS_DIR = Path(__file__).parent / "Maps"


@dataclass(frozen=True)
class MapDefinition:
    name: str
    modified_maps: tuple[str, ...]


def discover_maps() -> list[MapDefinition]:
    definitions: list[MapDefinition] = []
    for path in sorted(MAPS_DIR.glob("*.json")):
        modified_maps = _read_modified_maps(path)
        definitions.append(
            MapDefinition(
                name=path.stem,
                modified_maps=tuple(modified_maps),
            ),
        )
    return definitions


def _read_modified_maps(path: Path) -> list[str]:
    try:
        with path.open(encoding="utf-8") as fp:
            data: dict[str, Any] = json.load(fp)
    except FileNotFoundError:
        logging.warning("Map file '%s' was not found", path)
        return []
    except Exception:  # noqa: BLE001
        logging.error(f"Failed to read map metadata from '{path}'")
        return []

    return [key.lower() for key in data]
