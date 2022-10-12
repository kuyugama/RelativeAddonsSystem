import json
from pathlib import Path


class AddonMeta:

    name: str
    version: str
    description: str
    author: str
    status: str
    requirements: list[dict[str, str]]

    def __init__(self, path: Path):
        self._path = path

        self._keys = []

        self.load()

    def get(self, name: str, default: object):
        if name not in self:
            return default

        return self[name]

    def set(self, name: str, value: object):
        json.dumps(value)

        if name not in self:
            self._keys.append(name)

        setattr(self, name, value)

    def __getitem__(self, item):
        if item not in self:
            raise KeyError(item)

        return getattr(self, item, None)

    def __setitem__(self, key, value):
        json.dumps(value)
        if key not in self:
            self._keys.append(key)
        setattr(self, key, value)

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