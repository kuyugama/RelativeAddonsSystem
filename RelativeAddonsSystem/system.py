import shutil
from pathlib import Path
import os
import json
import warnings

from . import libraries
from .addon import Addon


class RelativeAddonsSystem:

    def __init__(self, addons_directory: str | Path, auto_install_requirements: bool = False):
        self.addon_with_requirements_problem = []
        self.already_checked_addons = []
        self.pip_libraries = []

        if not isinstance(addons_directory, Path):
            addons_directory = Path(addons_directory)

        if not addons_directory.exists():
            addons_directory.mkdir(parents=True)

        if addons_directory.is_file():
            raise ValueError("Addons directory cannot be a file")

        self._directory = addons_directory

        self.auto_install_requirements = auto_install_requirements

    @property
    def directory(self):
        """
        **Path to addons directory**

        :return: pathlib.Path
        """
        return self._directory

    def get_addon_by_name(self, name: str | Addon) -> Addon:
        """
        **You can get addon by its name**

        :param name: name of addon. You can pass here the object of the addon and get the same object
        :return: return addon object
        """
        if isinstance(name, Addon):
            return name
        elif not isinstance(name, str):
            raise ValueError("Expected str, but got {}".format(name.__class__.__name__))

        addons_list = list(
            filter(
                lambda filename: (self.directory / filename).is_dir(),
                os.listdir(self.directory)
            )
        )

        for addon_dir_name in addons_list:
            addon_dir_name: str
            addon_path = self.directory / addon_dir_name
            addon_dir_list = os.listdir(addon_path)

            if "__init__.py" not in addon_dir_list and "addon.json" not in addon_dir_list:
                continue

            with open(addon_path / "addon.json", encoding="utf8") as f:
                addon_info = json.load(f)

            if addon_info["name"] == name:
                return Addon(path=addon_path, meta_path=addon_path / "addon.json")

    def check_addon_requirements(
            self,
            name: str | Addon,
            alert: bool = False
    ) -> bool:
        """
        **Automatically checks the requirements of addon**

        :param name: name of addon. You can pass here the addon name or its "object"(dictionary {path: ..., info: ...})
        :param alert: bool. Alert if problem
        :return: bool. True if addon requirements is satisfied
        """

        addon = self.get_addon_by_name(name)

        if not addon:
            return False

        if addon.meta["name"] in self.already_checked_addons:
            return True

        return addon.check_requirements(alert=alert)

    def install_addon_requirements(self, name: str | Addon) -> list[str]:
        """
        **Automatic installation of addon requirements if required**

        :param name: name of addon. You can pass here addon name or its "object"(dictionary {path: ..., info: ...})
        :return: list of installed libraries
        """

        addon = self.get_addon_by_name(name)

        if addon is None:
            raise ValueError("Cannot find this addon.")

        return addon.install_requirements()

    def get_all_addons(self, status: str | None = None) -> list[Addon]:
        """
        **Get all addons**

        :param status: str, optional. Filter addons by its status.
        :return: list of addons RelativeAddonsSystem.Addon
        """

        addons_list = list(
            filter(
                lambda filename: (self.directory / filename).is_dir(),
                os.listdir(self.directory)
            )
        )

        addons = []

        for addon_name in addons_list:
            addon_name: str
            addon_path = self.directory / addon_name

            addon_files = os.listdir(addon_path)

            if "__init__.py" not in addon_files or "addon.json" not in addon_files:
                continue

            with open(addon_path / "addon.json", encoding="utf8") as f:
                addon_meta = json.load(f)

            if (
                    "name" not in addon_meta
                    or "description" not in addon_meta
                    or "version" not in addon_meta
                    or "author" not in addon_meta
            ):
                warnings.warn(
                    "addon [{}] does not have required fields: name/description/version/author".format(
                        addon_path.absolute())
                )
                continue
            addon = Addon(path=addon_path, meta_path=addon_path / "addon.json")

            if "status" not in addon.meta:
                addon.meta["status"] = "disabled"
                addon.meta.save()

            if status:
                if addon.meta.get("status", "") != status:
                    continue

            if "requirements" not in addon.meta:
                addon.meta["requirements"] = []
                addon.meta.save()

            if self.auto_install_requirements and not self.check_addon_requirements(
                    addon_meta["name"],
                    alert=True
            ):
                self.install_addon_requirements(addon)

            addons.append(addon)

        if self.auto_install_requirements:
            libraries.get_installed_libraries(force=True)

        return addons

    def get_enabled_addons(self) -> list[Addon]:
        """
        **Get the enabled addons**

        :return: list of the addons objects
        """

        return self.get_all_addons(status="enabled")

    def get_disabled_addons(self) -> list[Addon]:
        """
        **Get disabled addons**

        :return: list of addons "objects"(dictionary {path: ..., info: ...})
        """

        return self.get_all_addons(status="disabled")

    def get_enabled_addons_as_python_modules(self) -> list[Addon]:
        """
        **Get enabled addons as python modules**

        :return: list of addons "objects"(dictionary {path: ..., info: ..., module: ...})
        """
        enabled_addons = self.get_enabled_addons()

        addons = []

        for addon in enabled_addons:
            if addon.meta["name"] in self.addon_with_requirements_problem:
                continue

            addon.get_module()

            addons.append(
                addon
            )

        return addons

    def get_disabled_addons_as_python_modules(self) -> list[Addon]:
        """
        **Get disabled addons as python modules**

        :return: list of addons objects
        """

        enabled_addons = self.get_disabled_addons()

        addons = []

        for addon in enabled_addons:
            if addon.meta["name"] in self.addon_with_requirements_problem:
                continue

            addon.get_module()

            addons.append(
                addon
            )

        return addons

    def get_addon_as_python_module(self, name: str | Addon) -> Addon:
        """
        **Get addon as python module**

        :param name: pass here the addon name or its object
        :return: addon object
        """
        addon = self.get_addon_by_name(name)

        if not addon:
            raise ValueError("Cannot find this addon")

        if name not in self.already_checked_addons:
            if name in self.addon_with_requirements_problem or not self.check_addon_requirements(name):
                raise ValueError("Requirements of addon not satisfied")

        addon.get_module()

        return addon

    def reload_addon(self, name: str | dict) -> Addon:
        """
        **Re-imports addon**

        :param name: name of addon or its object
        :return: addon object
        """
        addon = self.get_addon_as_python_module(name)
        addon.reload_module()

        if addon.meta["name"] in self.already_checked_addons:
            self.already_checked_addons.remove(addon.meta["name"])

        return addon

    def enable_addon(self, name: str | Addon) -> Addon:
        """
        **enable addon**

        :param name: name of addon. You can also pass here the object of addon
        :return: same addon
        """
        addon = self.get_addon_by_name(name)

        if not addon:
            raise ValueError("Cannot find addon \"{name}\"".format(name=name))

        if not self.check_addon_requirements(addon):
            raise ValueError("Requirements of {name} not satisfied!".format(name=addon.meta["name"]))

        addon.enable()

        if addon.meta["name"] in self.already_checked_addons:
            self.already_checked_addons.remove(addon.meta["name"])

        return addon

    def disable_addon(self, name: str) -> Addon:
        """
        **disable addon**

        :param name: name of addon. You can also pass here the object of addon
        :return: same addon
        """
        addon = self.get_addon_by_name(name)

        if not addon:
            raise ValueError("Cannot find this addon")

        addon.disable()

        if addon.meta["name"] in self.already_checked_addons:
            self.already_checked_addons.remove(addon.meta["name"])

        return addon

    def remove_addon(self, name: str) -> bool:
        """
        **remove addon**

        :param name: name of addon. You can also pass here the addon object
        :return: bool. True if successfully removed addon
        """

        addon = self.get_addon_by_name(name)

        if not addon:
            raise ValueError("Cannot find this addon")

        shutil.rmtree(addon.path, ignore_errors=True)

        if addon.meta["name"] in self.already_checked_addons:
            self.already_checked_addons.remove(addon.meta["name"])

        return True

    def pack_addon(self, name: str) -> str | None:
        """
        **Make tar-archive from addon(for sharing)**

        :param name: the name of the addon. You can also pass here the addon object
        :return: Path to addon or if it is not found - None
        """
        addon = self.get_addon_by_name(name)

        if not addon:
            return

        return shutil.make_archive(name, "tar", addon.path)
