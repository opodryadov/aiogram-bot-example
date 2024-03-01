import abc
from typing import Any


class BaseCache(abc.ABC):
    async def get_from_cache(self, key: str) -> Any | None:
        pass

    async def put_to_cache(self, key: str, value: Any) -> None:
        pass
