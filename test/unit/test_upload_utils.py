import os
import io
import shutil

import pytest

from werkzeug.datastructures import FileStorage
from utils.upload_utils import (
    save_file,
    check_zip_size,
    validate_zip_contents,
    InvalidFileError,
    LargeZipError,
    FolderAlreadyExistsError,
    SaveZipFileError,
)


TEST_FOLDER = "test/unit/test_upload_utils"


def create_in_memory_file(filename: str) -> FileStorage:
    """
    Creates a FileStorage object from a string.

    Args:
        content (str): content of file
        filename (str): name of file

    Returns:
        FileStorage: in-memory FileStorage object
    """
    file = io.BytesIO()
    file.write(b"testing")
    file.seek(0)
    return FileStorage(file, filename=filename)


@pytest.mark.parametrize(
    "file_name",
    [
        ("test_file.txt"),
        ("test_file.jpg"),
        ("test_file.zip"),
    ],
)
def test_save_file(file_name: str):
    """
    Tests that save_file saves a zipfile to the correct location.
    """
    file = create_in_memory_file(file_name)
    os.mkdir(TEST_FOLDER)
    try:
        save_file(file, TEST_FOLDER)
        file_path = os.path.join(TEST_FOLDER, file.filename)
        assert os.path.exists(file_path)
    finally:
        shutil.rmtree(TEST_FOLDER)


def test_save_file_no_folder():
    """
    Tests that save_file raises an error if the folder does not exist.
    """
    file = create_in_memory_file("test_file.txt")
    with pytest.raises(SaveZipFileError):
        save_file(file, TEST_FOLDER)
