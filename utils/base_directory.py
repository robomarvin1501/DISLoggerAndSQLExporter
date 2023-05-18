import platform


def get_base_directory() -> str:
    """
    Gets the base directory, since that is different on different operating systems
    :return: str : path for the base directory
    """
    current_os = platform.system()

    base_dir = ""
    if current_os == "Linux":
        base_dir = "~/"
    elif current_os == "Windows":
        base_dir = "C:/"
    else:
        print(f"ERROR: Current OS {current_os} is currently unsupported.")
        print("This is because I don't know where to put the base dir")
        print("If you do, please fork and create a pull request adding this functionality.")
        exit(1)
    return base_dir
