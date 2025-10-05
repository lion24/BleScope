class InteractionError(Exception):
    """Base exception for interaction errors"""
    pass

class DeviceNotConnectedError(InteractionError):
    """Raised when trying to interact with a disconnected device"""
    pass

class CharacteristicNotFoundError(InteractionError):
    """Raised when a characteristic is not found"""
    pass

class CharacteristicNotReadableError(InteractionError):
    """Raised when trying to read a non-readable characteristic"""
    pass

class CharacteristicNotWritableError(InteractionError):
    """Raised when trying to write to a non-writable characteristic"""
    pass

class CharacteristicNotNotifiableError(InteractionError):
    """Raised when trying to enable notifications on a non-notifiable characteristic"""
    pass
