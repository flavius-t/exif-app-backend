import os
import stat


PERMISSIONS = 0o644


def restrict_file_permissions(folder_path: str):
    """
    Set file permissions to read-write for owner, read for group and others.
    Intended for use on folders containing files uploaded by application users.

    Args:
        folder_path (str): path to folder containing files to be restricted
    """
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        current_permissions = os.stat(file_path).st_mode
        new_permissions = current_permissions | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        os.chmod(file_path, new_permissions)
