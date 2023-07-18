import pytest
import os
import json
import shutil

from PIL import Image

from test.testing_utils import create_image_files
from utils.extract_meta import _extract_metadata, _remove_exif, _write_to_json


TEST_FOLDER = "test_extract_meta_folder"


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
            assert img.info.get('exif') is not None

            _remove_exif(img)
            assert img.info.get('exif') is None
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
