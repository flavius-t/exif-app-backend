import pytest
import os
import json
import shutil
from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

from PIL import Image

from test.testing_utils import create_image_files
from test.integration.test_upload import TEST_VALID_MULTIPLE
from utils.extract_meta import (
    _extract_metadata,
    _remove_exif,
    _write_to_json,
    extract_metadata,
    ExtractMetaError,
)


TEST_FOLDER = "test_extract_meta_folder"
TEST_IMG_1 = os.path.join(TEST_VALID_MULTIPLE, "DSC_2250.jpg")
TEST_IMG_2 = os.path.join(TEST_VALID_MULTIPLE, "DSC_2241.jpg")


@pytest.mark.parametrize(
    "filename, metadata",
    [
        ("image.jpg", {"width": 800, "height": 600}),
        ("photo.png", {"width": 1024, "height": 768}),
        ("data.json", {"name": "John", "age": 30}),
        ("data.txt", {}),
    ],
)
def test_write_to_json(filename, metadata):
    os.mkdir(TEST_FOLDER)
    base_name = os.path.splitext(filename)[0]
    file_path = os.path.join(TEST_FOLDER, filename)
    expected_output_file_path = os.path.join(TEST_FOLDER, f"{base_name}_meta.json")

    try:
        _write_to_json(file_path, metadata)
        assert os.path.isfile(expected_output_file_path)

        with open(expected_output_file_path, "r") as output_file:
            output_data = json.load(output_file)

        assert output_data == metadata
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FOLDER)


@pytest.mark.parametrize("metadata", [None, 1, 1.0, True, [], ()])
def test_write_to_json_invalid_args(metadata):
    os.mkdir(TEST_FOLDER)
    try:
        file_path = os.path.join(TEST_FOLDER, "image.jpg")

        with pytest.raises(TypeError):
            _write_to_json(file_path, metadata)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FOLDER)


def set_mock_exif(img):
    exif_data = {
        "Make": "Camera Manufacturer",
        "Model": "Camera Model",
        "DateTimeOriginal": "2022:01:01 12:00:00",
    }
    img.info["exif"] = exif_data
    img.save("image_with_exif.jpg")
    img.seek(0)


def test_remove_exif():
    os.mkdir(TEST_FOLDER)
    try:
        create_image_files(1, TEST_FOLDER)
        file_path = os.path.join(TEST_FOLDER, "test_file_0.jpg")

        with open(file_path, "rb") as f:
            img = Image.open(f)
            img.filename = os.path.basename(file_path)
            set_mock_exif(img)
            assert img.info.get("exif") is not None

            _remove_exif(img)
            assert img.info.get("exif") is None
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FOLDER)
        os.remove("image_with_exif.jpg")
        os.remove("test_file_0.jpg")


def test_remove_exif_invalid_image():
    invalid_image = "not_an_image"

    with pytest.raises(TypeError) as exc_info:
        _remove_exif(invalid_image)

    assert str(exc_info.value) == "Image must be a PIL Image object"


def test_extract_metadata_creates_meta_file():
    os.mkdir(TEST_FOLDER)
    try:
        test_img_name = os.path.basename(TEST_IMG_1)
        test_img_name_no_ext = os.path.splitext(test_img_name)[0]
        cpy_dest = os.path.join(TEST_FOLDER, test_img_name)
        shutil.copy(TEST_IMG_1, cpy_dest)

        _extract_metadata(cpy_dest)

        meta_file = os.path.join(TEST_FOLDER, f"{test_img_name_no_ext}_meta.json")
        assert os.path.isfile(meta_file)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(TEST_FOLDER)


@pytest.mark.parametrize("arg", [
    ("invalid_image_path"),
    (1),
    ]
)
def test_extract_metadata_raises(arg):
    with pytest.raises(ExtractMetaError):
        _extract_metadata(arg)


@pytest.mark.parametrize(
    "folder_contents",
    [
        ([]),
        (["file1.jpg"]),
        (["file1.png"]),
        (["file1.jpg", "file2.jpg"]),
        (["file1.png", "file2.jpg"]),
    ],
)
def test_extract_metadata_folder(folder_contents):
    with patch("utils.extract_meta._extract_metadata") as mock_extract, patch(
        "os.listdir"
    ) as mock_listdir:
        mock_listdir.return_value = folder_contents
        extract_metadata("dummy_folder")
        assert mock_extract.call_count == len(folder_contents)
