import os
from pathlib import Path

from .storage import Storage


class RelativeAddonsSystemCache(Storage):
    _instance = None
    DATA_KEY = "addons_data"
    STATES_KEY = "addons_states"

    def __init__(self, path: Path):
        super().__init__(path)
        self.initialize({self.DATA_KEY: {}, self.STATES_KEY: {}})

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance

        inst = object.__new__(cls)

        inst.__init__(*args, **kwargs)

        cls._instance = inst

        return inst

    @classmethod
    def get_instance(cls) -> "RelativeAddonsSystemCache":
        return cls._instance

    def get_addon_data(self, addon: "Addon"):
        return self.get(self.DATA_KEY, {}).get(addon.meta.name, {})

    def update_addon_data(self, data: dict, addon: "Addon"):
        if self.DATA_KEY not in self:
            self.set(self.DATA_KEY, {})

        addons_data = self.get(self.DATA_KEY, {})

        addons_data.update({addon.meta.name: data})

        self.save()

    def addon_updated(self, addon: "Addon", update_state: bool = False):
        addons_states: dict[str, dict] = self.get(self.STATES_KEY, {})

        system_addon_modified_time = os.path.getmtime(addon.path)

        addon_state = addons_states.get(addon.meta.name, None)

        saved_addon_modified_time = addon_state["last_modified"] if addon_state else None

        if update_state:
            self.update_addon_state(addon)

        return saved_addon_modified_time != system_addon_modified_time

    def update_addon_state(self, addon: "Addon"):
        addons_states: dict[str, dict] = self.get(self.STATES_KEY, {})

        system_addon_modified_time = os.path.getmtime(addon.path)

        addon_state = addons_states.get(addon.meta.name, None)

        if not addon_state:
            addons_states[addon.meta.name] = dict(
                last_modified=system_addon_modified_time
            )
        else:
            addon_state["last_modified"] = system_addon_modified_time

        self.save()

    def remove_addons(self, *addons: "Addon"):
        cached_states = self.get(self.STATES_KEY, {})
        cached_data = self.get(self.DATA_KEY, {})

        for addon in addons:
            if addon.meta.name in cached_data:
                del cached_data[addon.meta.name]

            if addon.meta.name in cached_states:
                del cached_states[addon.meta.name]

        self.save()
