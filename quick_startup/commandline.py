from argparse import ArgumentParser
import os
import struct
from time import sleep
from uuid import UUID

import ctypes
from ctypes import wintypes

from mods_base import get_pc

from unrealsdk.logging import misc as log

from typing import Sequence

CHARACTER_ARG = "-Character"


def get_character_arg() -> str | None:
    # The winapi to get the current process's command line arguments.
    GetCommandLineW = ctypes.windll.kernel32.GetCommandLineW
    GetCommandLineW.restype = wintypes.LPWSTR
    GetCommandLineW.argtypes = ()

    # The winapi to parse the command line argument string into an array.
    CommandLineToArgvW = ctypes.windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    CommandLineToArgvW.argtypes = (wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int))

    # Create an int and use it to store the number of args while parsing them.
    c_argc = ctypes.c_int()
    argv: Sequence[str] = CommandLineToArgvW(GetCommandLineW(), ctypes.byref(c_argc))
    argv = argv[: c_argc.value]

    # Since BL2's existing launch arguments don't follow standard convention, we manually pick out
    # our argument into a sequence to pass to argparse.
    for index, arg in enumerate(argv):
        if arg.lower() == CHARACTER_ARG.lower():
            next_index = index + 1
            if len(argv) > next_index and not argv[next_index].startswith("-"):
                character_argv = ("-c", argv[next_index])
            else:
                character_argv = ("-c", "")
            break
        if arg.lower().startswith(CHARACTER_ARG.lower() + "="):
            character_argv = ("-c" + arg[len(CHARACTER_ARG) :],)
            break
    else:
        character_argv = ()

    arg_parser = ArgumentParser(exit_on_error=False)
    arg_parser.add_argument("-c")
    parsed_args = arg_parser.parse_args(character_argv)

    return vars(parsed_args)["c"]


def save_id_for_character_arg(character_arg: str) -> int | None:
    savegame_manager = get_pc().GetWillowGlobals().GetWillowSaveGameManager()

    # This function needs to be performed synchronously, as it is used when hooking the game's
    # startup save selection in order to inject our own.
    get_pc().GetSaveGameList()
    while savegame_manager.AsyncResult[0] == 1:
        sleep(0.1)

    if character_arg.lower().endswith(".sav"):
        for savedata in savegame_manager.SaveDataLoadedFromList:
            savedata_file = os.path.basename(savedata.FilePath)
            if savedata_file.lower() == character_arg.lower():
                log("Matched filename")
                return savedata.SaveGameFileId

    try:
        character_guid = UUID(character_arg)
    except ValueError:
        character_guid = None
    if character_guid is not None:
        # Convert our GUID's bytes into the same little-endian int representation as BL2's.
        guid_ints = struct.unpack_from("<iiii", character_guid.bytes_le)
        for savedata in savegame_manager.SaveDataLoadedFromList:
            savedata_guid = savedata.SaveGuid
            if guid_ints == (savedata_guid.A, savedata_guid.B, savedata_guid.C, savedata_guid.D):
                log("Matched GUID")
                return savedata.SaveGameFileId

    for savedata in savegame_manager.SaveDataLoadedFromList:
        if savedata.UICharacterName.casefold() == character_arg.casefold():
            log("Matched character name")
            return savedata.SaveGameFileId

    log(f"No character found for '{character_arg}'")
