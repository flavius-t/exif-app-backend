import os
import zipfile
import shutil
from io import BytesIO
from unittest.mock import patch

import pytest
from exif import (
    app,
    ERR_NO_ZIP,
    ERR_NON_IMAGE_FILE,
    ERR_FILE_NAME,
    ERR_NO_FILES,
    ERR_ZIP_SIZE_LIMIT,
    ERR_ZIP_CORRUPT,
    ERR_TEMP_FOLDER,
    ERR_UNZIP_FILE,
    ERR_EXTRACT_META,
)
from test.testing_utils import create_file_of_size
from utils.upload_utils import ZIP_SIZE_LIMIT_MB
from utils.constants import UPLOAD_FOLDER


UPLOAD_ENDPOINT = "/upload"

TEST_FILES_FOLDER = os.path.join("test", "testing_files")

TEST_VALID_SINGLE = os.path.join(TEST_FILES_FOLDER, "valid_single")
TEST_VALID_MULTIPLE = os.path.join(TEST_FILES_FOLDER, "valid_multiple")
TEST_INVALID_ONLY = os.path.join(TEST_FILES_FOLDER, "invalid_only")
TEST_INVALID_MIX = os.path.join(TEST_FILES_FOLDER, "invalid_mix")
TEST_EMPTY = os.path.join(TEST_FILES_FOLDER, "empty")

TEST_IMAGE_1 = os.path.join(TEST_VALID_SINGLE, "DSC_2233.jpg")


@pytest.fixture(name="client")
def create_app():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("file_path", [TEST_IMAGE_1])
def test_upload_file_no_zip(client, file_path):
    with open(file_path, "rb") as file:
        response = client.post(
            UPLOAD_ENDPOINT,
            data={"file": (file, "image.jpg", "image/jpeg")},
            content_type="multipart/form-data",
        )

    assert response.status_code == ERR_NO_ZIP[1]
    assert ERR_NO_ZIP[0] in str(response.data)


def test_upload_misnamed_file(client):
    with open(TEST_IMAGE_1, "rb") as file:
        response = client.post(
            UPLOAD_ENDPOINT,
            data={"image": (file, "image.jpg", "image/jpeg")},
            content_type="multipart/form-data",
        )

    assert response.status_code == ERR_FILE_NAME[1]
    assert ERR_FILE_NAME[0] in str(response.data)


def test_upload_missing_files(client):
    response = client.post(UPLOAD_ENDPOINT)

    assert response.status_code == ERR_NO_FILES[1]
    assert ERR_NO_FILES[0] in str(response.data)


def zip_folder_and_post(client, folder_path):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    zip_buffer.seek(0)

    response = client.post(
        UPLOAD_ENDPOINT,
        data={"file": (zip_buffer, "images.zip", "application/zip")},
        content_type="multipart/form-data",
    )

    return response


@pytest.mark.parametrize(
    "folder_path",
    [
        TEST_VALID_SINGLE,
        TEST_VALID_MULTIPLE,
    ],
)
def test_upload_valid_zipped(client, folder_path):
    response = zip_folder_and_post(client, folder_path)

    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    assert response.headers["Content-Disposition"] == "attachment; filename=images.zip"
    assert response.headers.get("X-Request-ID") is not None

    with zipfile.ZipFile(BytesIO(response.data)) as zip_file:
        assert len(zip_file.namelist()) == len(os.listdir(folder_path)) * 2
        for file in os.listdir(folder_path):
            assert file in zip_file.namelist()
            assert f"{file.split('.')[0]}_meta.json" in zip_file.namelist()


@pytest.mark.parametrize("folder_path", [TEST_INVALID_ONLY, TEST_INVALID_MIX])
def test_upload_invalid_zipped(client, folder_path):
    response = zip_folder_and_post(client, folder_path)

    assert response.status_code == ERR_NON_IMAGE_FILE[1]
    assert ERR_NON_IMAGE_FILE[0] in str(response.data)


def test_upload_large_zip(client):
    zip_buffer = create_file_of_size(ZIP_SIZE_LIMIT_MB + 1)

    response = client.post(
        UPLOAD_ENDPOINT,
        data={"file": (zip_buffer, "images.zip", "application/zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == ERR_ZIP_SIZE_LIMIT[1]
    assert ERR_ZIP_SIZE_LIMIT[0] in str(response.data)


def test_upload_corrupted_zip(client):
    zip_buffer = BytesIO(b"corrupted")

    response = client.post(
        UPLOAD_ENDPOINT,
        data={"file": (zip_buffer, "images.zip", "application/zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == ERR_ZIP_CORRUPT[1]
    assert ERR_ZIP_CORRUPT[0] in str(response.data)


def test_temp_folder_already_exists(client):
    mock_req_id = "12345"

    try:
        with patch("uuid.uuid4", return_value=mock_req_id):
            temp_folder = os.path.join(UPLOAD_FOLDER, mock_req_id, "images")
            os.makedirs(temp_folder)
            assert os.path.exists(temp_folder)

            response = zip_folder_and_post(client, TEST_VALID_SINGLE)

            assert response.status_code == ERR_TEMP_FOLDER[1]
            assert ERR_TEMP_FOLDER[0] in str(response.data)
    finally:
        shutil.rmtree(os.path.join(UPLOAD_FOLDER, mock_req_id))


def test_upload_empty_zip(client):
    response = zip_folder_and_post(client, TEST_EMPTY)

    assert response.status_code == ERR_UNZIP_FILE[1]
    assert ERR_UNZIP_FILE[0] in str(response.data)


def test_upload_invalid_image_file(client):
    file_name = "invalid_image.jpg"
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(file_name, b"invalid image data")

    zip_buffer.seek(0)

    response = client.post(
        UPLOAD_ENDPOINT,
        data={"file": (zip_buffer, "images.zip", "application/zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == ERR_EXTRACT_META[1]
    assert ERR_EXTRACT_META[0] in str(response.data)
