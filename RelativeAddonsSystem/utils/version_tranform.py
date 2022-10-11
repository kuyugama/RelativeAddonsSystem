
def to_library_version(raw_version: str | int | float):
    if isinstance(raw_version, (int, float)):
        return str(raw_version)

    version = ""
    for char in raw_version:
        if char != "*":
            version += char
        else:
            version = version[:-1]
            break

    if len(version.split(".")) < 2:
        version += '.0'

    return version