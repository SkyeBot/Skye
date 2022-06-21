
from __future__ import annotations
from functools import wraps


import sys
import logging

from typing import (Tuple, Optional, Dict, TYPE_CHECKING, Any)
from .errors import BotExceptions
from .helper import convert_bytes

if TYPE_CHECKING:
    from core.bot import SkyeBot


__all__: Tuple[str, ...] = (
    'CacheManager',
    'Cache'
)


class CacheManager:
    __slots__: Tuple[str, ...] = (
        'bot',
        '_cache'
    )

    def __init__(self, bot) -> None:
        self.bot: SkyeBot = bot
        self._cache: Dict[Any, Dict] = {}

    @property
    def count(self) -> str:
        raw = [
            f"{item.replace('_', ' ').title()}: {len(list(value.values()))}" for item, value in self._cache.items()
        ]

        tables = "\n".join(raw)

        total = sum(len(v) for v in self._cache.values())
        size = convert_bytes(sys.getsizeof(self._cache))
        
        return (
            f"\nStoring total of {total} rows in my cache with size of {size}"
            f"\n{tables}"
        )

    @property
    def raw(self) -> Dict:
        return self._cache

    def __repr__(self) -> str:
        return "DaPanda.helpers.CacheManger"

    def _exists(self, name: Any) -> bool:
        return name in list(self._cache.keys())

    def create(self, name: Any, data: Optional[Dict] = None) -> Cache:
        if self._exists(name):
            raise BotExceptions(f"There is already cache named {name!r}")

        self._cache[name] = data or {}
        return Cache(
            self.bot,
            name,
            data
        )

    def create_if_not_exist(self, name: Any, data: Optional[Dict] = None) -> Cache:
        if self._exists(name):
            return Cache(
                self.bot,
                name,
                self._cache.get(name, {})
            )

        self._cache[name] = data or {}
        return Cache(
            self.bot,
            name,
            self._cache[name]
        )

    def delete(self, name: Any) -> None:
        if not self._exists(name):
            raise BotExceptions(f"Cache named {name!r} doesnt exist!")
        del self._cache[name]

    def get(self, name: Any) -> Optional[Cache]:
        if (data := self._cache.get(name, None)):
            return Cache(self.bot, name, data)
        return None

    def add(self, name: Any, data: Dict) -> None:
        if not self._exists(name):
            raise BotExceptions(f"Cache named {name!r} does not exist")
        else:
            (self._cache[name]).update(data)
            return Cache(self.bot, name, self._cache[name])
        
    def remove(self, name: Any, key: Any) -> None:
        if not self._exists(name):
            raise BotExceptions(f"Cache named {name!r} does not exist!")

        (self._cache[name]).pop(key, None)

    def find(self, cache: str, item: Any) -> Optional[Cache]:
        if not (_cache := self.get(cache)):
            return None
        return _cache.get(item)

    def clear(self) -> None:
        """Reset the `_cache` object ot its defautl state"""
        self._cache = {}

    def set(self, name: Any, data: Dict) -> None:
        self._cache[name] = data

    def update(self, name: Any, key: Any, new: Any) -> None:
        if not self._exists(name):
            raise BotExceptions(f"Cache {name!r} doesn't exist!")
        
        try:
            self._cache[name][key] = new
        except KeyError:
            raise BotExceptions(f"Key {key!r} doesn't exist in {name!r}")

class Cache:
    __slots__ = (
        'bot',
        'title', 
        'data',
        'manager'
    )

    def __init__(self, bot:SkyeBot, title: str, data: Dict) -> None:
        self.bot = bot
        self.title = title
        self.data = data
        self.manager = self.bot.cache

    def __str__(self) -> str:
        return str(self.data)

    def get(self, name: Any) -> Optional[Any]:
        return self.data.get(name, None)

    def add(self, data: Dict) -> None:
        (self.manager._cache[self.title]).update(data)
        return Cache(self.bot, self.title, self.manager._cache[self.title])

    def remove(self, name: Any) -> None:
        if not self.manager._cache[self.title].pop(name, None):
            raise BotExceptions(f"{name!r} doesn\'t exist in the current cache")

    def set(self, name: Any, data: Dict) -> None:
        """
        Do stuff
        """
        self.manager._cache[name] = data



def cache(maxsize=128):
    cache = {}

    def decorator(func):
        @wraps(func)
        def inner(*args, no_cache=False, **kwargs):
            if no_cache:
                return func(*args, **kwargs)

            key_base = "_".join(str(x) for x in args)
            key_end = "_".join(f"{k}:{v}" for k, v in kwargs.items())
            key = f"{key_base}-{key_end}"

            if key in cache:
                return cache[key]

            res = func(*args, **kwargs)

            if len(cache) > maxsize:
                del cache[list(cache.keys())[0]]
                cache[key] = res

            return res
        return inner
    return decorator


def async_cache(maxsize=128):
    cache = {}

    def decorator(func):
        @wraps(func)
        async def inner(*args, no_cache=False, **kwargs):
            if no_cache:
                return await func(*args, **kwargs)

            key_base = "_".join(str(x) for x in args)
            key_end = "_".join(f"{k}:{v}" for k, v in kwargs.items())
            key = f"{key_base}-{key_end}"

            if key in cache:
                return cache[key]

            res = await func(*args, **kwargs)

            if len(cache) > maxsize:
                del cache[list(cache.keys())[0]]
                cache[key] = res

            return res
        return inner
    return decorator