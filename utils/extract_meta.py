"""
Helper functions for extracting metadata from images.

Functions:
    extract_metadata(folder_path: str) -> None
    _extract_metadata(file_path: str) -> None
    _remove_exif(img: Image) -> None
    _write_to_json(filename: str, metadata: dict) -> None

Exceptions:
    ExtractMetaError(Exception)
"""

import json
import os
import logging
from PIL import ExifTags, Image, UnidentifiedImageError


log = logging.getLogger(__name__)
logging.getLogger("PIL").setLevel(logging.INFO)


class ExtractMetaError(Exception):
    """
    Exception raised for errors related to extracting metadata from images.
    """

    def __init__(self, message: str, underlying_exception: Exception = None):
        """
        Args:
            message (str): explanation of the error
            underlying_exception (Exception): the exception that caused this exception
        """
        self.message = "Error occurred while extracting metadata from image: " + message
        self.underlying_exception = underlying_exception
        super().__init__(message)

    def __str__(self):
        if self.underlying_exception:
            return f"{self.message}\nUnderlying Exception: {str(self.underlying_exception)}"
        return self.message


def extract_metadata(folder_path: str) -> None:
    """
    Extracts and removes metadata from all images in a folder.

    Args:
        folder_path (str): path to folder containing images

    Raises:
        ValueError: if any file in folder is not an image file
    """
    for file in os.listdir(folder_path):
        _extract_metadata(os.path.join(folder_path, file))


def _extract_metadata(file_path: str) -> None:
    """
    Extracts and removes metadata from an image file.

    Args:
        file_path (str): path to image file

    Raises:
        ExtractMetaError: if an error occurs while extracting metadata
    """
    log.debug(f"Extracting metadata from {file_path}")

    metadata = {}

    try:
        with Image.open(file_path) as img:
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["size"] = img.size

            if img._getexif() is not None:
                metadata["exif"] = {
                    ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS
                }

                for k, v in metadata["exif"].items():
                    if not isinstance(v, str) and not isinstance(v, int):
                        metadata["exif"][k] = str(v)

                if hasattr(img, "info"):
                    _remove_exif(img)

            _write_to_json(img.filename, metadata)
    except (AttributeError, FileNotFoundError, TypeError, UnidentifiedImageError) as e:
        raise ExtractMetaError(f"Error while extracting metadata from {file_path}", e)

    return None


def _remove_exif(img: Image) -> None:
    """
    Removes exif data from an image.

    Args:
        img (Image): PIL Image object

    Raises:
        TypeError: if img is not a PIL Image object
    """
    if not isinstance(img, Image.Image):
        raise TypeError("Image must be a PIL Image object")

    if "exif" in img.info:
        img.info.pop("exif")
        img.save(img.filename)


def _write_to_json(filename: str, metadata: dict):
    """
    Writes image metadata to a json file.

    Args:
        filename (str): path to image file

    Raises:
        TypeError: if metadata is not a dictionary
    """
    if not isinstance(metadata, dict):
        raise TypeError("Metadata must be a dictionary")

    base_name = os.path.splitext(filename)[0]
    output_file_path = f"{base_name}_meta.json"
    with open(output_file_path, "w") as output_file:
        json.dump(metadata, output_file, indent=4)
