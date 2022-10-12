## Relative Addons System
**This is special system which allow you to manage your addons**

**Addon** is a folder with ``addon.json`` and ``__init__.py`` files

**_Example:_**
```python
from pathlib import Path

from RelativeAddonsSystem import RelativeAddonsSystem, Addon, AddonMeta

# Init addons system
system = RelativeAddonsSystem(Path(__file__).parent / "addons")

# return list of Addon objects
addons: list[Addon] = system.get_all_addons()

if len(addons) < 1:
    print("No addons found")
else:
    for addon in addons:
        # loaded meta(AddonMeta) from ADDON_DIR/addon.json
        meta: AddonMeta = addon.meta
        
        print("Working with", meta.name, "at", addon.path.absolute())
        
        # Check dependencies
        if not addon.check_requirements(alert=False):
            print("Installing addon dependencies")
            # Install dependencies
            installed: list[str] = addon.install_requirements()
            print("Successfully installed addon dependencies (", ", ".join(installed), ")")
        else:
            print("Addon dependencies already satisfied")
        
        # Get addon module
        module = addon.module # ADDON_DIR / __init__.py module
        ...
```

**In this example, we have listed all addons and install their dependencies if they are not installed**

**You can also disable or enable addons:**

```python
from pathlib import Path

from RelativeAddonsSystem import RelativeAddonsSystem, Addon

# Init addons system
system = RelativeAddonsSystem(Path(__file__).parent / "addons")

addons: list[Addon] = system.get_enabled_addons() # get all enabled addons

if len(addons) > 0:
    addon: Addon = addons[0] # first addon from list
    addon.disable() # disable addon
    
    ...
    
    addon.enable() # enable addon
```

**_Or import, reimport(Useful when you updated your addon) module:_**
```python
from pathlib import Path

from RelativeAddonsSystem import RelativeAddonsSystem, Addon

# Init addons system
system = RelativeAddonsSystem(Path(__file__).parent / "addons")

addons: list[Addon] = system.get_enabled_addons() # get all enabled addons

if len(addons) > 0:
    addon: Addon = addons[0] # first addon from list
    
    module = addon.module
    
    ... # Work with module

    # Reimport module
    module = addon.reload_module()
    
    ... # Work with module
```

**_You can also change the meta in your code:_**
```python
from pathlib import Path

from RelativeAddonsSystem import RelativeAddonsSystem, Addon, AddonMeta

# Init addons system
system = RelativeAddonsSystem(Path(__file__).parent / "addons")

addons: list[Addon] = system.get_enabled_addons() # get all enabled addons

if len(addons) > 0:
    addon: Addon = addons[0] # first addon from list
    
    meta: AddonMeta = addon.meta

    meta.set("version", "1.2")

    meta.save()
```
