import os

"""
Efficiently list all files and files in subdirectories.
"""
def list_all_files(root_dir):
    w = os.walk(root_dir)
    for (dir, _, filenames) in w:
        for f in filenames:
            # List the file under the dir
            print(os.path.join(dir, f))
            # You operation here ...
            pass

def delete_all_files_starting_with_dot(root_dir):
    w = os.walk(root_dir)
    for (dir, _, filenames) in w:
        for f in filenames:
            print(os.path.join(dir, f))
            # Delete all files starting with "."
            if f.startswith("."):
                os.remove(os.path.join(dir, f))
                print(f"Delete {os.path.join(dir, f)}")