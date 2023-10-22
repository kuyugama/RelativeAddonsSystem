import json
from pathlib import Path
from typing import Any


class AddonMeta:
    """
    AddonMeta File representation

    Usage:

    meta = AddonMeta("path/to/addon.json")

    print(meta.version) # Print version from addon meta

    meta.set("meta_option", "value") # Set "value" for meta_option in addon meta

    meta.save() # Save addon meta

    print(meta.meta_option) # Print meta_option from addon meta
    """
    name: str
    version: str
    description: str
    author: str
    status: str | None
    requirements: list[dict[str, str]] | None

    def __init__(self, path: Path):
        self._path = path

        self._keys = []

        self.load()

    def get(self, name: str, default: Any = None) -> int | str | dict | list | float | bool:
        if name not in self:
            return default

        return self[name]

    def set(self, name: str, value: object):
        json.dumps(value)

        if name not in self:
            self._keys.append(name)

        setattr(self, name, value)

    def remove(self, name: str):
        if name not in self:
            raise KeyError(name)

        delattr(self, name)
        self._keys.remove(name)

    def __getitem__(self, item):
        if item not in self:
            raise KeyError(item)

        return getattr(self, item, None)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, item):
        return item in self._keys

    def load(self):

        with open(self._path, encoding="utf8") as meta_file:

            info = json.load(meta_file)

            self._keys = list(info.keys())

            for name, value in info.items():
                setattr(self, name, value)

    def save(self):
        with open(self._path, "w", encoding="utf8") as meta_file:
            json.dump(
                {
                    name: self[name]
                    for name in self._keys
                },
                meta_file,
                ensure_ascii=False,
                indent=4
            )
