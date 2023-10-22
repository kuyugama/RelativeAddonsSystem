import importlib
import sys
import types


def recursive_reload_module(module: types.ModuleType, exclude: tuple[str] = ...) -> types.ModuleType:
    if not isinstance(module, types.ModuleType):
        raise ValueError("Unsupported type of module")

    if not isinstance(exclude, tuple):
        exclude = ()

    exclude += (
        *sys.builtin_module_names,
        "os",
        "builtins",
        "__main__",
        "ntpath"
    )

    if module.__name__ in exclude:
        return module

    for value in vars(module).values():
        if not isinstance(value, types.ModuleType):
            continue

        recursive_reload_module(value, exclude)

    return importlib.reload(module)
