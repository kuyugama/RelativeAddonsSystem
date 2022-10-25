import importlib
import json
import shutil
import types
import warnings
from pathlib import Path

from .metadata import AddonMeta
from .configuration import AddonConfig
from .. import libraries, utils


class MetadataError(BaseException):
    pass


class Addon:
    def __init__(self, path: Path, meta_path: Path = None, module=None):

        if meta_path is None:
            meta_path = path / "addon.json"

        if not isinstance(meta_path, Path):
            raise MetadataError(
                "Cannot recognize metadata of addon at {path}".format(
                    path=path.absolute()
                )
            )

        self._meta = AddonMeta(meta_path)
        self.path = path
        self._module = module
        self._config = None

        self._module_path = self.path.relative_to(Path().absolute())
        self._config_path = self.path / (self.meta.name + ".config")

    @property
    def meta(self):
        if not self._meta:
            if not self.path / "addon.json":
                raise MetadataError(
                    "Cannot find metadata file of addon at {path}".format(
                        path=self.path.absolute()
                    )
                )

            with open(self.path / "addon.json") as info:
                self._meta = AddonMeta(**json.load(info))

        return self._meta

    def __str__(self):
        return f"Addon(name={repr(self.meta.get('name', 'None'))}, path={repr(self.path.absolute())})"

    def enable(self):
        self.meta["status"] = "enabled"

        with open(self.path / "addon.json", "w", encoding="utf8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=4)

    def disable(self):
        self.meta["status"] = "disabled"

        with open(self.path / "addon.json", "w", encoding="utf8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=4)

    def remove(self):
        """
        **Removes addon**
        """
        shutil.rmtree(self.path)
        del self

    @property
    def module(self):
        if not self._module:
            self._module = importlib.import_module(
                str(self._module_path)
                .replace("\\", ".")
                .replace("/", ".")
            )

        return self._module

    @module.setter
    def module(self, value):
        self._module = value

    def get_module(self):
        return self.module

    def set_module(self, module):
        self.module = module

    def reload_module(self):
        if not self._module:
            self.get_module()

        # for name, module in vars(self._module).items():
        #     if isinstance(module, types.ModuleType):
        #         setattr(self._module, name, importlib.reload(module))

        self.set_module(utils.recursive_reload_module(self._module))

        return self.module

    def pack(self) -> str:
        """
        **Make zip archive from addon**

        :return: str - path to archive
        """
        return shutil.make_archive(self.meta["name"], "zip", root_dir=self.path)

    def get_config(self):

        if not self._config:
            self._config = AddonConfig(self._config_path)

        return self._config

    def check_requirements(self, alert: bool = True):
        """
        **Automatically checks the requirements of addon**

        :param alert: bool. Alert if problem
        :return: bool. True if addon requirements is satisfied
        """

        installed_libraries = libraries.get_installed_libraries()

        for requirement in self.meta.get("requirements", []):
            if requirement["name"].lower() not in installed_libraries:
                if alert:
                    warnings.warn(
                        "addon [{}] requires not installed library [{}] with version {}".format(
                            self.meta["name"],
                            requirement["name"],
                            requirement["version"],
                        )
                    )
                return False

            if utils.check_version(
                requirement["version"], installed_libraries[requirement["name"].lower()]
            ):
                continue
            else:
                if alert:
                    warnings.warn(
                        "addon [{}] requires library [{}] with version {}, "
                        "but current version of library is {}".format(
                            self.meta["name"],
                            requirement["name"],
                            requirement["version"],
                            installed_libraries[requirement["name"].lower()],
                        )
                    )
                return False

        return True

    def install_requirements(self) -> list[str]:
        """
        **Automatic installation of addon requirements if required**

        :return: list of installed libraries
        """

        addon_requirements = self.meta.get("requirements", [])

        return libraries.install_libraries(addon_requirements)
