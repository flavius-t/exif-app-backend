import os
from io import BytesIO
from zipfile import ZipFile

import pytest
from exif import app, ERR_NO_ZIP
from utils.zip import zip_files


@pytest.fixture(name="client")
def create_app():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


TEST_IMAGES_FOLDER = os.path.join("test", "images")
TEST_IMAGE_1 = os.path.join(TEST_IMAGES_FOLDER, "DSC_2233.jpg")


def test_upload_single_img_no_zip(client):
    with open(TEST_IMAGE_1, "rb") as img:
        response = client.post(
            "/upload",
            data={"image": (img, "image.jpg")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert bytes(ERR_NO_ZIP[0], "utf-8") in response.data


def test_upload_images(client):
    zip_buffer = zip_files(TEST_IMAGES_FOLDER)
    response = client.post(
        "/upload",
        data={"file": (zip_buffer, "images.zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    assert response.headers["Content-Disposition"] == "attachment; filename=images.zip"
    assert response.headers["X-Request-Id"] is not None

    with ZipFile(BytesIO(response.data)) as zip_file:
        assert len(zip_file.namelist()) == len(os.listdir(TEST_IMAGES_FOLDER)) * 2
        for file in os.listdir(TEST_IMAGES_FOLDER):
            assert file in zip_file.namelist()
            assert f"{file.split('.')[0]}_meta.json" in zip_file.namelist()
