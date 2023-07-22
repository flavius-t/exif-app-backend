"""
Unit tests for the mime_type module.
"""

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
def test_get_mime_type_legal(file_path: str, expected_mime_type: str):
    """
    Test that get_mime_type returns the correct MIME type for a given file.
    """
    assert get_mime_type(file_path) == expected_mime_type


def test_get_mime_type_invalid():
    """
    Test that get_mime_type raises an error if the file type is not supported.
    """
    with pytest.raises(ValueError) as e:
        get_mime_type("test.txt")
        assert "is not an accepted file type" in str(e.value)
