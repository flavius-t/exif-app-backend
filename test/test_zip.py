import pytest
import os
import shutil
import zipfile
from contextlib import nullcontext as does_not_raise

from test.testing_utils import create_text_files, create_image_files, create_mixed_files
from utils.zip import zip_files, unzip_file
from utils.zip import ZipError


TEST_FILES_FOLDER = "test_zip"
ZIP_EXTRACTION_FOLDER = "test_zip_extract"


@pytest.mark.parametrize(
    "create_files, num_files",
    [(create_text_files, 3), (create_mixed_files, 3)],
)
def test_zip_files_illegal(create_files, num_files):
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
def test_zip_files_legal(num_files):
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
    with pytest.raises(ZipError) as e:
        zip_files("invalid_folder")
        assert "FileNotFound" in str(e.value)


@pytest.mark.parametrize(
    "num_files, err", [(3, does_not_raise()), (1, does_not_raise()), (0, pytest.raises(ZipError))]
)
def test_unzip_files(num_files, err):
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
    with pytest.raises(ZipError) as e:
        unzip_file("bad_path", "bad_path")
        assert "Zip file not found" in str(e.value)


def test_unzip_non_zip_file():
    os.mkdir(TEST_FILES_FOLDER)
    try:
        file_path = os.path.join(TEST_FILES_FOLDER, "test.txt")
        with open(file_path, "w") as f:
            f.write("testing")
        with pytest.raises(ZipError) as e:
            unzip_file(file_path, "bad_path")
            assert "Zip file is corrupted" in str(e.value)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FILES_FOLDER)
