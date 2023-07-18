import pytest
import os
import json
import shutil

from utils.extract_meta import _extract_metadata, _remove_exif, _write_to_json

TEST_FOLDER = "test_extract_meta_folder"

@pytest.mark.parametrize(
    "filename, metadata",
    [
        ("image.jpg", {"width": 800, "height": 600}),
        ("photo.png", {"width": 1024, "height": 768}),
        ("data.json", {"name": "John", "age": 30}),
        ("data.txt", {}),
    ]
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
