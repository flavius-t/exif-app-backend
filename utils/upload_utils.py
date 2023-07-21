import os
import zipfile
import logging
from io import BytesIO

from werkzeug.datastructures import FileStorage

from utils.constants import UPLOAD_FOLDER, ZIP_NAME


log = logging.getLogger(__name__)


ALLOWED_EXTENSIONS = set(["jpg", "jpeg", "png"])
ZIP_SIZE_LIMIT_MB = 100  # 100 MB


class InvalidFileError(Exception):
    pass


class LargeZipError(Exception):
    pass


class FolderAlreadyExistsError(Exception):
    pass


class SaveZipFileError(Exception):
    pass


def validate_zip_contents(zip_file: BytesIO) -> None:
    """
    Validates that all files in a zipfile are image files.

    Args:
        zip_file (FileStorage): zipfile to validate

    Raises:
        InvalidFileError: if any file in zipfile is not an image file
        BadZipFile: if zipfile is corrupted (or likely file pointer is not at start of file)
    """
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            for file in zip_ref.namelist():
                _, file_extension = os.path.splitext(file)
                if not file_extension[1:] in ALLOWED_EXTENSIONS:
                    raise InvalidFileError(f"File {file} is not an image file")
    except zipfile.BadZipFile as e:
        log.error(f"BadZipFile: zipfile {file} is corrupted -> {e}")
        raise e


def check_zip_size(zip_file: BytesIO) -> None:
    """
    Checks that zipfile is under the size limit.

    Args:
        zip_file (BytesIO): zipfile to check

    Raises:
        LargeZipError: if zipfile is over the size limit
    """
    if zip_file.getbuffer().nbytes > ZIP_SIZE_LIMIT_MB * 1000000:
        raise LargeZipError(f"Zip file exceeds size limit of {ZIP_SIZE_LIMIT_MB} bytes")


def save_file(file: FileStorage, folder: str) -> str:
    """
    Saves an in-memory file to a folder.

    Args:
        file (FileStorage): file to save
        filename (str): name of file
        folder (str): folder to save file to

    Returns:
        str: path to saved file
    """
    # zip_path = os.path.join(folder, ZIP_NAME)

    file_path = os.path.join(folder, file.filename)

    try:
        file.save(file_path)
    except FileNotFoundError as e:
        log.error(
            f"FileNotFoundError: failed to save file '{file.filename}' - target directory '{folder}' likely does not exist"
        )
        raise SaveZipFileError(f"Failed to save file '{file.filename}' -> {e}") from e

    file.close()
    return file_path


def create_temp_folder(req_id: str) -> tuple[str, str]:
    """
    Creates a temporary folder for storing images.

    Args:
        req_id (str): request id to use for naming folder

    Returns:
        tuple[str, str]: path to base folder, path to images folder

    Raises:
        FolderAlreadyExistsError: if folder with same name already exists
    """
    base_folder = f"{UPLOAD_FOLDER}/{req_id}"
    imgs_folder = f"{base_folder}/images"
    try:
        os.makedirs(imgs_folder)
    except OSError:
        raise FolderAlreadyExistsError(f"Folder {imgs_folder} already exists")

    return base_folder, imgs_folder
