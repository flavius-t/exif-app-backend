import zipfile
import os
import io
import logging


log = logging.getLogger(__name__)


MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "json": "application/json"
}


def get_mime_type(file_path: str):
    """
    Returns the MIME type of a file based on its extension.

    Args:
        file_path (str): path to file
    
    Raises:
        ValueError: if file is not accepted file type (image or json)
    """
    _, file_extension = os.path.splitext(file_path)
    mime_type = MIME_TYPES.get(file_extension[1:])
    if mime_type is None:
        raise ValueError(f'{file_path} is not an accepted file type')
    return mime_type


class ZipError(Exception):
    """
    Exception raised for errors related to zipping files.
    """
    def __init__(self, message, underlying_exception=None):
        self.message = 'Error occurred while zipping images: ' + message
        self.underlying_exception = underlying_exception
        super().__init__(message)

    def __str__(self):
        if self.underlying_exception:
            return f"{self.message}\nUnderlying Exception: {str(self.underlying_exception)}"
        return self.message


def unzip_file(zip_path, extract_dir):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile as e:
        log.error(f'BadZipFile: zipfile {zip_path} is corrupted -> {e}')
        raise ZipError('Zip file is corrupted', e)
    except FileNotFoundError as e:
        log.error(f'FileNotFoundError: could not find file {zip_path} -> {e}')
        raise ZipError('Zip file not found', e)
    except zipfile.LargeZipFile as e:
        log.error(f'LargeZipFile: zip file exceeds limits -> {e}')
        raise ZipError('Zip file exceeds size limit', e)
    except NotADirectoryError as e:
        log.error(f'NotADirectoryError: {extract_dir} is not a directory -> {e}')
        raise ZipError('Extraction directory invalid', e)
    except OSError as e:
        log.error(f'OSError: could not extract zipfile {zip_path} -> {e}')
        raise ZipError('', e)


def zip_files(folder_path: str):
    # Ensure folder path is valid
    if not os.path.exists(folder_path):
        log.error(f"Folder '{folder_path}' does not exist.")
        raise ZipError(f"Could not zip images. Folder '{folder_path}' does not exist.")

    # write files to zipfile in-memory
    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through all files and subdirectories
            for root, _, files in os.walk(folder_path):
                for file in files:
                    # Get absolute file path
                    file_path = os.path.join(root, file)

                    # Add file to zip
                    zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))

                    # set mime type
                    mime_type = get_mime_type(file)
                    log.debug(f'Setting mime type of {file} to {mime_type}')
                    zipinfo = zipf.getinfo(file)
                    zipinfo.comment = mime_type.encode('utf-8')
    except FileNotFoundError as e:
        log.error(f'FileNotFoundError: could not find file {file_path} -> {e}')
        raise ZipError('Fle not found', e)
    except zipfile.LargeZipFile:
        log.error(f'LargeZipFile: zip file exceeds limits -> {e}')
        raise ZipError('Zip file exceeds size limit', e)
    except ValueError as e:
        log.error(f'ValueError: attempted to zip illegal file -> {e}')
        raise ZipError('Illegal file', e)

    buffer.seek(0)

    return buffer
