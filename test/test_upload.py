import pytest
from flask.testing import FlaskClient
from exif import app, ERR_NO_ZIP

@pytest.fixture(name='client')
def create_app():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

TEST_IMAGE_1 = "./test/images/DSC_2233.jpg"

def test_upload_single_img_no_zip(client):
    with open(TEST_IMAGE_1, "rb") as img:
        response = client.post(
            "/upload",
            data={"image": (img, "image.jpg")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert bytes(ERR_NO_ZIP[0], 'utf-8') in response.data
