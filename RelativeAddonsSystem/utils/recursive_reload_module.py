import importlib
import types


def recursive_reload_module(module: types.ModuleType):
    if not isinstance(module, types.ModuleType):
        raise ValueError("Unsupported type of module")

    for value in vars(module).values():
        if not isinstance(value, types.ModuleType):
            continue

        recursive_reload_module(value)

    return importlib.reload(module)
