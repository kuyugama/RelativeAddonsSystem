def check_version_correctness(version: str | int | float):
    if isinstance(version, (int, float)):
        return True

    if not len(version):
        return False

    if version.startswith("."):
        return False

    if version.isdigit() or version == "*":
        return True

    if all(map(lambda x: x != "", version.split("."))):
        return True


def check_version(required_version: str | int| float, library_version: str | int | float):
    if not check_version_correctness(required_version):
        raise ValueError("Incorrect required version type: {}".format(required_version))
    elif not check_version_correctness(library_version):
        raise ValueError("Incorrect library version type: {}".format(library_version))

    if isinstance(required_version, (int, float)):
        required_version = str(required_version)

    if isinstance(library_version, (int, float)):
        library_version = str(library_version)

    required_version_parted = required_version.split(".")
    library_version_parted = library_version.split(".")

    if len(required_version_parted) > len(library_version_parted):
        return False

    for part_req, part_lib in zip(required_version_parted, library_version_parted):
        if part_req == part_lib:
            continue
        elif part_req == "*":
            return True
        else:
            return False

    return True
