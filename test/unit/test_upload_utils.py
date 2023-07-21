import os
import io
import shutil
from contextlib import nullcontext as does_not_raise

import pytest

from werkzeug.datastructures import FileStorage
from utils.upload_utils import (
    save_file,
    check_zip_size,
    validate_zip_contents,
    create_temp_folder,
    InvalidFileError,
    LargeZipError,
    FolderAlreadyExistsError,
    SaveZipFileError,
    ZIP_SIZE_LIMIT_MB,
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


def create_file_of_size(size_in_mb: int) -> io.BytesIO:
    size_in_bytes = size_in_mb * 1000 * 1000
    in_memory_file = io.BytesIO()
    in_memory_file.write(b"\x00" * size_in_bytes)
    in_memory_file.seek(0)
    return in_memory_file


@pytest.mark.parametrize("file_size", [(1), (2), (10), (56), (99), (100)])
def test_create_file_of_size(file_size):
    """
    Tests that create_file_of_size correctly creates a file of the correct size.
    """
    file = create_file_of_size(file_size)
    assert file.getbuffer().nbytes / 1000000 == file_size


@pytest.mark.parametrize(
    "file_size, err",
    [
        (1, does_not_raise()),
        (100, does_not_raise()),
        (101, pytest.raises(LargeZipError)),
    ],
)
def test_check_zip_size(file_size, err):
    """
    Tests that check_zip_size correctly checks the size of a zipfile.
    """
    file = create_file_of_size(file_size)
    with err:
        check_zip_size(file)


def test_create_temp_folder():
    """
    Tests that create_temp_folder correctly creates a temporary folder.
    """
    req_id = "test_req_id"
    base_folder, imgs_folder = create_temp_folder(req_id)
    try:
        assert os.path.exists(base_folder)
        assert os.path.exists(imgs_folder)
    finally:
        shutil.rmtree(base_folder)


def test_create_temp_folder_raises():
    """
    Tests that create_temp_folder raises an error if the folder already exists.
    """
    req_id = "test_req_id"
    base_folder, _ = create_temp_folder(req_id)
    with pytest.raises(FolderAlreadyExistsError):
        create_temp_folder(req_id)
    shutil.rmtree(base_folder)
