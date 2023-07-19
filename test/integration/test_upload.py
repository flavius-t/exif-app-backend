import os
import zipfile
from io import BytesIO

import pytest
from exif import app, ERR_NO_ZIP, ERR_NON_IMAGE_FILE


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
            data={"image": (file, "image.jpg")},
            content_type="multipart/form-data",
        )

    assert response.status_code == ERR_NO_ZIP[1]
    assert ERR_NO_ZIP[0] in str(response.data)


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
        data={"file": (zip_buffer, "images.zip")},
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
