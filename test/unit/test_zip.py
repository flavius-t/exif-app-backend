"""
Unit tests for zip.py
"""

import pytest
import os
import shutil
import zipfile
from io import BytesIO
from contextlib import nullcontext as does_not_raise

from test.testing_utils import create_text_files, create_image_files, create_mixed_files
from utils.zip import zip_files, unzip_file
from utils.zip import ZipError, UnzipError


TEST_FILES_FOLDER = "test_zip"
ZIP_EXTRACTION_FOLDER = "test_zip_extract"


@pytest.mark.parametrize(
    "create_files, num_files",
    [(create_text_files, 3), (create_mixed_files, 3)],
)
def test_zip_files_illegal(create_files, num_files: int):
    """
    Test that zip_files raises an error if a non-image file is zipped.

    Args:
        create_files (function): function to create files
        num_files (int): number of files to create
    """
    os.mkdir(TEST_FILES_FOLDER)
    try:
        create_files(num_files, TEST_FILES_FOLDER)
        with pytest.raises(ZipError) as e:
            zip_files(TEST_FILES_FOLDER)
            assert "Illegal file" in str(e.value)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FILES_FOLDER)


@pytest.mark.parametrize("num_files", [3, 1, 0])
def test_zip_files_legal(num_files: int):
    """
    Test that zip_files correctly zips a folder of image files.

    Args:
        num_files (int): number of files to create
    """
    os.mkdir(TEST_FILES_FOLDER)
    try:
        create_image_files(num_files, TEST_FILES_FOLDER)
        buffer = zip_files(TEST_FILES_FOLDER)
        assert buffer is not None
        with zipfile.ZipFile(buffer, "r") as zip_ref:
            file_list = zip_ref.namelist()
            assert len(file_list) == num_files
            for file_name in file_list:
                assert file_name in os.listdir(TEST_FILES_FOLDER)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FILES_FOLDER)


def test_zip_files_invalid_folder():
    """
    Test that zip_files raises an error if the folder does not exist.
    """
    with pytest.raises(ZipError) as e:
        zip_files("invalid_folder")
        assert "FileNotFound" in str(e.value)


@pytest.mark.parametrize(
    "num_files, err", [(3, does_not_raise()), (1, does_not_raise()), (0, pytest.raises(UnzipError))]
)
def test_unzip_files(num_files: int, err):
    """
    Test that unzip_files correctly unzips a zipfile.

    Args:
        num_files (int): number of mock files to create
        err (Exception): expected exception
    """
    os.mkdir(TEST_FILES_FOLDER)
    try:
        with err:
            create_image_files(num_files, TEST_FILES_FOLDER)
            buffer = zip_files(TEST_FILES_FOLDER)
            assert buffer is not None
            # write buffer zipfile to disk
            zip_path = os.path.join(TEST_FILES_FOLDER, "test.zip")
            with open(zip_path, "wb") as f:
                f.write(buffer.getvalue())
            assert os.path.exists(zip_path)
            # unzip files
            extract_dir = os.path.join(TEST_FILES_FOLDER, ZIP_EXTRACTION_FOLDER)
            unzip_file(zip_path, extract_dir)
            assert os.path.exists(extract_dir)
            assert len(os.listdir(extract_dir)) == num_files
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FILES_FOLDER)


def test_unzip_files_bad_path():
    """
    Test that unzip_files raises an error if the zipfile does not exist.
    """
    with pytest.raises(UnzipError) as e:
        unzip_file("bad_path", "bad_path")
        assert "Zip file not found" in str(e.value)


def test_unzip_non_zip_file():
    """
    Test that unzip_files raises an error if the file is not a zipfile.
    """
    os.mkdir(TEST_FILES_FOLDER)
    try:
        file_path = os.path.join(TEST_FILES_FOLDER, "test.txt")
        with open(file_path, "w") as f:
            f.write("testing")
        with pytest.raises(UnzipError) as e:
            unzip_file(file_path, "bad_path")
            assert "Zip file is corrupted" in str(e.value)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FILES_FOLDER)


@pytest.mark.parametrize(
    "file_names, expected",
    [
        (["illegal -- file.txt"], ["illegal--file.txt"]),
        (["..illegal.txt"], ["illegal.txt"]),
    ],
)
def test_unzip_sanitization(file_names: list[str], expected: list[str]):
    """
    Test that unzip_files correctly sanitizes the file names.
    """
    os.mkdir(TEST_FILES_FOLDER)
    try:
        # write new files to disk
        for file in file_names:
            file_path = os.path.join(TEST_FILES_FOLDER, file)
            with open(file_path, "w") as f:
                f.write("testing")

        # create buffer zipfile with new files
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_ref:
            for file in file_names:
                file_path = os.path.join(TEST_FILES_FOLDER, file)
                zip_ref.write(file_path, file)

        # write buffer zipfile to disk
        zip_path = os.path.join(TEST_FILES_FOLDER, "test.zip")
        with open(zip_path, "wb") as f:
            f.write(buffer.getvalue())
        assert os.path.exists(zip_path)

        # unzip files and check that the file names are sanitized
        extract_dir = os.path.join(TEST_FILES_FOLDER, ZIP_EXTRACTION_FOLDER)
        unzip_file(zip_path, extract_dir)
        assert os.path.exists(extract_dir)
        assert os.listdir(extract_dir) == expected
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FILES_FOLDER)
