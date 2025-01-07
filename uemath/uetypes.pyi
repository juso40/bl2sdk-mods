from unrealsdk import unreal

class UEVector(unreal.WrappedStruct):
    X: float
    Y: float
    Z: float

class UERotator(unreal.WrappedStruct):
    Pitch: int
    Yaw: int
    Roll: int