from enum import IntEnum

from mods_base import get_pc, hook, options
import unrealsdk
from unrealsdk import make_struct
from unrealsdk.unreal import UObject
from unrealsdk.hooks import Block

ReplaceHTMLMarkup = unrealsdk.find_class("Actor").ClassDefaultObject.ReplaceHTMLMarkup
WillowSaveGameManager = unrealsdk.find_class("WillowSaveGameManager").ClassDefaultObject
GetTimePlayedString = WillowSaveGameManager.GetHumanReadableStringFromTimePlayed
GetSaveDateString = WillowSaveGameManager.GetHumanReadableStringFromSaveDateString


class UniqueSaveID(IntEnum):
    NoCharacter = -1
    LastCharacter = -2


def character_button_pressed(_1: options.ButtonOption) -> None:  # noqa: ANN001
    LoadCharacter_Start.enable()
    LoadCharacter_SavesUpdated.enable()
    LoadCharacter_RefreshList.enable()
    LoadCharacter_SlotClicked.enable()
    LoadCharacter_TryDelete.enable()
    LoadCharacter_OnClose.enable()

    globals_def = get_pc().GetWillowGlobals().GetGlobalsDefinition()
    loadcharactermovie_path = globals_def.LoadCharacterMovieDefinition._path_name()
    get_pc().PlayGfxMovieDefinition(loadcharactermovie_path)


quick_mode = options.BoolOption(
    "Safe Mode",
    True,
    description="Starts the game once everything is loaded. If false, skips everything.",
)

save_id = options.HiddenOption[int]("Save ID", UniqueSaveID.NoCharacter)

character_button = options.ButtonOption(
    "Choose Startup Character...",
    description="Select a character to immediately start the game with after it has loaded.",
    on_press=character_button_pressed,
)


@hook("WillowGame.WillowGFxLobbyLoadCharacter:Start")
def LoadCharacter_Start(obj: UObject, _2, _3, _4) -> None:  # noqa: ANN001
    obj.Priority = 255


@hook("WillowGame.WillowGFxLobbyLoadCharacter:SavesUpdated")
def LoadCharacter_SavesUpdated(obj: UObject, _2, _3, _4) -> type[Block]:  # noqa: ANN001
    obj.DisplayedCharacterDataList = [
        make_struct(
            "LoadCharacterData",
            CharName="<font color='#CCFFFF'>None</font>",
            SaveDataId=UniqueSaveID.NoCharacter,
        ),
        make_struct(
            "LoadCharacterData",
            CharName="<font color='#CCFFFF'>Last Played</font>",
            SaveDataId=UniqueSaveID.LastCharacter,
        ),
    ] + [
        make_struct(
            "LoadCharacterData",
            CharClass=savegame.ClassName,
            CharLevel=savegame.ExpLevel,
            CharName=ReplaceHTMLMarkup(savegame.UICharacterName)[0],
            CharPlayedTime=GetTimePlayedString(savegame.TotalPlayTime),
            CharPlayedTimeInt=savegame.TotalPlayTime,
            CharSaveDate=GetSaveDateString(savegame.LastSaveDate),
            PlayThrough=obj.ResolvePlaythrough(savegame.LastPlaythroughNumber + 1),
            ActiveMission=obj.ResolveMission(savegame.ActiveMissionNumber),
            PlotMission=obj.ResolveMission(savegame.PlotMissionNumber),
            SaveGuid=savegame.SaveGuid,
            SaveDataId=savegame.SaveGameFileId,
        )
        for savegame in obj.SaveGameHelper.SaveGames
    ]

    obj.TopSlotDataIndex = 0
    obj.RefreshCharacterList()
    obj.SelectedDataIndex = 0

    gfx_header = obj.LoadCharacterLobby.GetObject("saveList").GetObject("loadCharHeader")
    gfx_header.SetText("Quick Startup Character")

    return Block


@hook("WillowGame.WillowGFxLobbyLoadCharacter:RefreshCharacterList")
def LoadCharacter_RefreshList(obj: UObject, _2, _3, _4) -> type[Block]:  # noqa: ANN001
    if obj.LoadCharacterLobby is None or obj.TopSlotDataIndex == -1:
        return Block

    obj.LoadCharacterLobby.ClearSlots()

    SetSlotData = obj.LoadCharacterLobby.SetSlotData
    level_format = obj.Localize("LoadCharacter", "LevelFormat", "WillowMenu")

    for slot_index in range(obj.AvailableSlots):
        data_index = slot_index + obj.TopSlotDataIndex
        if data_index >= len(obj.DisplayedCharacterDataList):
            break

        savedata = obj.DisplayedCharacterDataList[slot_index + obj.TopSlotDataIndex]

        SetSlotData(
            slot_index,
            savedata.CharName,
            savedata.CharClass,
            (
                ""
                if savedata.SaveDataId < 0
                else level_format.replace(r"%level%", str(savedata.CharLevel))
            ),
            save_id.value == savedata.SaveDataId,
        )

    obj.LoadCharacterLobby.SetScrollArrows(
        obj.TopSlotDataIndex > 0,
        obj.TopSlotDataIndex + obj.AvailableSlots < len(obj.DisplayedCharacterDataList),
    )
    obj.SetTipText(False)

    return Block


@hook("WillowGame.WillowGFxLobbyLoadCharacter:OnSlotClicked")
def LoadCharacter_SlotClicked(obj: UObject, _2, _3, _4) -> type[Block]:  # noqa: ANN001
    save_id.value = obj.DisplayedCharacterDataList[obj.SelectedDataIndex].SaveDataId

    if (mod := save_id.mod) != None:
        mod.save_settings()

    obj.BeginClose()
    return Block


@hook("WillowGame.WillowGFxLobbyLoadCharacter:TryDeleteSelectedCharacter")
def LoadCharacter_TryDelete(obj: UObject, _2, _3, _4) -> type[Block]:  # noqa: ANN001
    return Block


@hook("WillowGame.WillowGFxLobbyLoadCharacter:OnClose")
def LoadCharacter_OnClose(_1, _2, _3, _4) -> None:  # noqa: ANN001
    LoadCharacter_Start.disable()
    LoadCharacter_SavesUpdated.disable()
    LoadCharacter_RefreshList.disable()
    LoadCharacter_SlotClicked.disable()
    LoadCharacter_TryDelete.disable()
    LoadCharacter_OnClose.disable()
