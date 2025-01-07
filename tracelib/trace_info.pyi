from unrealsdk.unreal import UObject, WrappedStruct

from uemath.uetypes import UEVector

class ImpactInfo(WrappedStruct):
    HitActor: UObject
    HitLocation: UEVector
    HitNormal: UEVector
    RayDir: UEVector
    StartTrace: UEVector
    HitInfo: TraceHitInfo
    EndTrace: UEVector

class TraceHitInfo(WrappedStruct):
    Material: UObject
    PhysMaterial: UObject
    Item: int
    LevelIndex: int
    BoneName: str
    HitComponent: UObject
