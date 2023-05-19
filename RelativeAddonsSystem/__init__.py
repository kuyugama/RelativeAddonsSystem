from .system import RelativeAddonsSystem
from .addon import Addon, AddonMeta
from . import utils
from .libraries import install_libraries, get_installed_libraries

__all__ = ["RelativeAddonsSystem", "Addon", "utils", "AddonMeta", "install_libraries", "get_installed_libraries"]

__version__ = "2.5.4"
