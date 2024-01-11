import os
import shutil


def delete(path: str):
    """Delete a file or a directory

    Args:
        path (str): a relative or absolute path for file or directory

    Raises:
        ValueError: Invalid path
    """
    # check if file or directory exists
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    else:
        raise ValueError(f"Path {path} is not a file or dir!")
