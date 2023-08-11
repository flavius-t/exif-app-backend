"""
This module contains functions for zipping and unzipping files.

Functions:
    unzip_file(zip_path: str, extract_dir: str) -> None
    zip_files(folder_path: str) -> BytesIO

Exceptions:
    UnzipError(Exception)
    ZipError(Exception)
"""

import zipfile
import os
import io
import logging

from utils.mime_type import get_mime_type
from utils.upload_utils import _sanitize_filename


log = logging.getLogger(__name__)


class UnzipError(Exception):
    """
    Exception raised for errors related to unzipping files.
    """

    def __init__(self, message: str, underlying_exception: Exception = None):
        self.message = "Error occurred while unzipping images: " + message
        self.underlying_exception = underlying_exception
        super().__init__(message)

    def __str__(self):
        if self.underlying_exception:
            return f"{self.message}\nUnderlying Exception: {str(self.underlying_exception)}"
        return self.message


class ZipError(Exception):
    """
    Exception raised for errors related to zipping files.
    """

    def __init__(self, message: str, underlying_exception: Exception = None):
        self.message = "Error occurred while zipping images: " + message
        self.underlying_exception = underlying_exception
        super().__init__(message)

    def __str__(self):
        if self.underlying_exception:
            return f"{self.message}\nUnderlying Exception: {str(self.underlying_exception)}"
        return self.message


def unzip_file(zip_path: str, extract_dir: str) -> None:
    """
    Unzips a zip file (on-disk) to a specified directory.

    Args:
        zip_path (str): path to zip file
        extract_dir (str): path to directory to extract zip file to

    Raises:
        UnzipError: if an error occurs while unzipping
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            if zip_ref.namelist() == []:
                raise UnzipError("Zip file is empty")
            for file_info in zip_ref.infolist():
                sanitized_filename = _sanitize_filename(file_info.filename)
                file_info.filename = sanitized_filename
                zip_ref.extract(file_info, path=extract_dir)
    except zipfile.BadZipFile as e:
        log.error(f"BadZipFile: zipfile {zip_path} is corrupted -> {e}")
        raise UnzipError("Zip file is corrupted", e)
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: could not find file {zip_path} -> {e}")
        raise UnzipError("Zip file not found", e)
    except zipfile.LargeZipFile as e:
        log.error(f"LargeZipFile: zip file exceeds limits -> {e}")
        raise UnzipError("Zip file exceeds size limit", e)
    except OSError as e:
        log.error(f"OSError: could not extract zipfile {zip_path} -> {e}")
        raise UnzipError("", e)


def zip_files(folder_path: str) -> io.BytesIO:
    """
    Zips all files in a folder (on-disk) to a zipfile (in-memory).

    Args:
        folder_path (str): path to folder containing files to zip

    Returns:
        io.BytesIO: in-memory zipfile

    Raises:
        ZipError: if an error occurs while zipping
    """
    if not os.path.exists(folder_path):
        log.error(f"Folder '{folder_path}' does not exist.")
        raise ZipError(f"Could not zip images. Folder '{folder_path}' does not exist.")

    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))

                    # set mime type
                    mime_type = get_mime_type(file)
                    log.debug(f"Setting mime type of {file} to {mime_type}")
                    zipinfo = zipf.getinfo(file)
                    zipinfo.comment = mime_type.encode("utf-8")
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: could not find file {file_path} -> {e}")
        raise ZipError("File not found", e)
    except zipfile.LargeZipFile:
        log.error(f"LargeZipFile: zip file exceeds limits -> {e}")
        raise ZipError("Zip file exceeds size limit", e)
    except ValueError as e:
        log.error(f"ValueError: attempted to zip illegal file -> {e}")
        raise ZipError("Illegal file", e)

    buffer.seek(0)

    return buffer
