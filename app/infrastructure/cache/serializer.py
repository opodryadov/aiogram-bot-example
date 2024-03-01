import abc
from typing import Any


class BaseSerializer(abc.ABC):
    @abc.abstractmethod
    def serialize(self, value: Any):
        pass

    @abc.abstractmethod
    def deserialize(self, str_value: str):
        pass
