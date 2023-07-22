"""
Helper methods for determining MIME types of files.

Functions:
    get_mime_type(file_path: str) -> str
"""

import os


MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "json": "application/json",
}


def get_mime_type(file_path: str) -> str:
    """
    Returns the MIME type of a file based on its extension.

    Args:
        file_path (str): path to file

    Returns:
        str: MIME type of file

    Raises:
        ValueError: if file is not accepted file type (image or json)
    """
    _, file_extension = os.path.splitext(file_path)
    mime_type = MIME_TYPES.get(file_extension[1:])
    if mime_type is None:
        raise ValueError(f"{file_path} is not an accepted file type")
    return mime_type
