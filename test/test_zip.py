import pytest
import os
import shutil
import zipfile

from PIL import Image

from utils.zip import zip_files
from utils.zip import ZipError


TEST_FILES_FOLDER = "test_zip"


def create_text_files(num_files):
    for i in range(num_files):
        file_path = os.path.join(TEST_FILES_FOLDER, f"test_file_{i}.txt")
        with open(file_path, "w") as f:
            f.write("testing")


def create_image_files(num_files):
    for i in range(num_files):
        file_path = os.path.join(TEST_FILES_FOLDER, f"test_file_{i}.jpg")
        image = Image.new("RGB", (500, 500), "white")
        image.save(file_path, "JPEG")


def create_mixed_files(num_files):
    create_text_files(num_files)
    create_image_files(num_files)


@pytest.mark.parametrize(
    "create_files, num_files",
    [(create_text_files, 3), (create_mixed_files, 3)],
)
def test_zip_files_illegal(create_files, num_files):
    os.mkdir(TEST_FILES_FOLDER)
    try:
        create_files(num_files)
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
        create_image_files(num_files)
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
