from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SensorData(_message.Message):
    __slots__ = ["luminosity", "temperature", "is_locked"]
    LUMINOSITY_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    IS_LOCKED_FIELD_NUMBER: _ClassVar[int]
    luminosity: str
    temperature: str
    is_locked: bool
    def __init__(self, luminosity: _Optional[str] = ..., temperature: _Optional[str] = ..., is_locked: bool = ...) -> None: ...

class ActuatorCommand(_message.Message):
    __slots__ = ["lock", "novo_nivel_luminosidade", "temperature", "equipment"]
    LOCK_FIELD_NUMBER: _ClassVar[int]
    NOVO_NIVEL_LUMINOSIDADE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    lock: bool
    novo_nivel_luminosidade: int
    temperature: int
    equipment: str
    def __init__(self, lock: bool = ..., novo_nivel_luminosidade: _Optional[int] = ..., temperature: _Optional[int] = ..., equipment: _Optional[str] = ...) -> None: ...
