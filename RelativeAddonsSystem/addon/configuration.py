import json
from pathlib import Path


class AddonConfig:

    def __init__(self, path: Path):
        self._path = path

        self._map = {}

        self.read()

    def read(self):
        if not self._path.exists():
            with open(self._path, "w", encoding="utf8") as file:
                json.dump({}, file, ensure_ascii=False, indent=4)

            self._map = {}
            return

        with open(self._path, "r", encoding="utf8") as file:
            self._map = json.load(file)

    def save(self):
        with open(self._path, "w", encoding="utf8") as file:
            json.dump(self._map, file, ensure_ascii=False, indent=4)

    def get(self, name: str, default: object=None):
        if name not in self._map:
            return default
        return self._map[name]

    def set(self, name: str, value: object):
        json.dumps(value)

        self._map[name] = value

    def keys(self):
        return self._map.keys()

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, item):
        if item not in self._map:
            raise KeyError(item)

        return self._map[item]
