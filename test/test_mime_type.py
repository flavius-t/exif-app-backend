import pytest

from utils.mime_type import get_mime_type, MIME_TYPES


@pytest.mark.parametrize(
    "file_path, expected_mime_type",
    [
        ("test.jpg", MIME_TYPES["jpg"]),
        ("test.jpeg", MIME_TYPES["jpeg"]),
        ("test.png", MIME_TYPES["png"]),
        ("test.json", MIME_TYPES["json"]),
    ],
)
def test_get_mime_type_legal(file_path, expected_mime_type):
    assert get_mime_type(file_path) == expected_mime_type


def test_get_mime_type_invalid():
    with pytest.raises(ValueError) as e:
        get_mime_type("test.txt")
        assert "is not an accepted file type" in str(e.value)
