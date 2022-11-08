import sys
from pathlib import Path
import subprocess
from contextvars import ContextVar

from RelativeAddonsSystem import utils


pip_executable = Path(sys.executable).parent / "pip"

installed_libraries = ContextVar("installed_libraries", default={})


def get_installed_libraries(force: bool = False) -> dict:
    """
    **Gets from the pip the installed libraries**

    :param force: Force read from pip
    :return: dictionary of libraries {library_name: version}
    """

    if force or len(installed_libraries.get()) == 0:
        pip_out = subprocess.getoutput(str(pip_executable.absolute()) + " freeze")

        libs = {}

        for lib in pip_out.splitlines():
            name, version = lib.lower().split("==")
            libs[name] = version

        installed_libraries.set(libs)

    return installed_libraries.get()


def install_libraries(libraries: list[dict[str, str]]) -> list[str]:
    names = []
    for requirement in libraries:
        if requirement["name"].lower() not in installed_libraries.get():
            name = requirement["name"].lower()
            if "version" in requirement and not requirement["version"] == "*":
                name += "==" + utils.version_tranform.to_library_version(requirement["version"])
            names.append(name)

        elif not utils.check_version(requirement["version"], installed_libraries.get()[requirement["name"].lower()]):
            name = requirement["name"].lower()
            if "version" in requirement and not requirement["version"] == "*":
                name += "==" + utils.version_tranform.to_library_version(requirement["version"])

            names.append(name)

    if len(names):
        out = subprocess.getoutput(
            str(pip_executable.absolute()) + " install " + " ".join(names)
        )
        if "ERROR" in out:
            raise RuntimeError("Error occurred while installing: {}".format(out))

    return names
