"""
Unit tests for upload_utils.py.
"""

import os
import io
import shutil
import zipfile
from contextlib import nullcontext as does_not_raise
from unittest.mock import patch

import pytest

from werkzeug.datastructures import FileStorage
from test.testing_utils import (
    create_text_files,
    create_image_files,
    create_mixed_files,
    create_file_of_size,
)
from utils.upload_utils import (
    save_file,
    check_zip_size,
    validate_zip_contents,
    create_temp_folder,
    InvalidFileError,
    LargeZipError,
    CreateTempFolderError,
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
    with pytest.raises(CreateTempFolderError):
        create_temp_folder(req_id)
    shutil.rmtree(base_folder)


@pytest.mark.parametrize(
    "create_files, num_files, err",
    [
        (create_text_files, 0, does_not_raise()),
        (create_image_files, 0, does_not_raise()),
        (create_mixed_files, 0, does_not_raise()),
        (create_image_files, 1, does_not_raise()),
        (create_text_files, 1, pytest.raises(InvalidFileError)),
        (create_mixed_files, 1, pytest.raises(InvalidFileError)),
    ],
)
def test_validate_zip_contents(create_files, num_files: int, err):
    """
    Tests that validate_zip_contents correctly validates a zipfile.
    """
    os.mkdir(TEST_FOLDER)

    try:
        create_files(num_files, TEST_FOLDER)

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, "w") as zip:
            for file in os.listdir(TEST_FOLDER):
                zip.write(os.path.join(TEST_FOLDER, file), file)

        zip_file.seek(0)

        with err:
            validate_zip_contents(zip_file)

        zip_file.close()
    finally:
        shutil.rmtree(TEST_FOLDER)


def test_validate_bad_zipfile():
    """
    Tests that validate_zip_contents correctly validates a zipfile.
    """
    os.mkdir(TEST_FOLDER)
    try:
        with patch('zipfile.ZipFile', side_effect=zipfile.BadZipFile()):
            corrupted_zip_file = io.BytesIO(b"Corrupted Zip Data")

            with pytest.raises(zipfile.BadZipFile):
                validate_zip_contents(corrupted_zip_file)
    finally:
        shutil.rmtree(TEST_FOLDER)
