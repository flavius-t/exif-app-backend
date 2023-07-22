"""
Flask app for uploading zip files containing images, extracting metadata from the images, and returning a zip file
"""

import shutil
import uuid
import logging
import zipfile
from io import BytesIO

from flask import Flask, request, send_file, make_response
from flask_cors import CORS

from utils.constants import ZIP_NAME
from utils.extract_meta import extract_metadata, ExtractMetaError
from utils.zip import unzip_file, zip_files, ZipError, UnzipError
from utils.upload_utils import (
    validate_zip_contents,
    check_zip_size,
    save_file,
    create_temp_folder,
    InvalidFileError,
    LargeZipError,
    FolderAlreadyExistsError,
    SaveZipFileError,
    ZIP_SIZE_LIMIT_MB,
)


app = Flask(__name__)
CORS(app)


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


ERR_NO_FILES = "No files contained in request", 400
ERR_FILE_NAME = "Expected attached file to be named 'file'", 400
ERR_NO_ZIP = "Request is missing zipfile", 400
ERR_TEMP_FOLDER = (
    "Internal error occured while processing images: failed to create temp folder",
    500,
)
ERR_NON_IMAGE_FILE = "Non-image file detected in upload", 400
ERR_UNZIP_FILE = (
    "Internal error occured while processing images: failed to unzip files",
    500,
)
ERR_ZIP_TO_MEMORY = (
    "Internal error occured while processing images: failed to zip files into memory",
    500,
)
ERR_EXTRACT_META = (
    "Internal error occured while processing images: failed to extract metadata from images",
    500,
)
ERR_ZIP_SIZE_LIMIT = (
    f"Zip file exceeds size limit of {ZIP_SIZE_LIMIT_MB} MB",
    400,
)
ERR_ZIP_CORRUPT = "Zip file is corrupted", 400
ERR_SAVE_ZIP = "Internal error occured while processing images: failed to save zipfile", 500


@app.route("/upload", methods=["POST"])
def handle_upload():
    """
    Handles image processing requests.
    """
    req_id = str(uuid.uuid4())
    log.info(f"Received new upload, assigning request_id {req_id}")

    if not request.files:
        log.error(f"request {req_id}: request contains no files")
        return ERR_NO_FILES

    file = request.files.get("file")

    if file is None:
        log.error(f"request {req_id}: expected file named 'file' not present")
        return ERR_FILE_NAME

    if file.mimetype != "application/zip":
        return ERR_NO_ZIP

    try:
        log.info(f"request {req_id}: creating temp folder")
        base_folder, imgs_folder = create_temp_folder(req_id)
    except FolderAlreadyExistsError as e:
        log.error(f"request {req_id}: could not create temp folder as it already exists -> {e}")
        return ERR_TEMP_FOLDER

    try:
        zip_buffer = BytesIO(file.read())
        log.info(f"request {req_id}: checking zipfile size")
        check_zip_size(zip_buffer)

        log.info(f"request {req_id}: validating zipfile contents")
        validate_zip_contents(zip_buffer)

        zip_buffer.close()
        file.seek(0)

        log.info(f"request {req_id}: saving zipfile to temp folder")
        zip_path = save_file(file, base_folder)

        log.info(f"request {req_id}: unzipping images")
        unzip_file(zip_path, imgs_folder)

        log.info(f"request {req_id}: extracting image metadata")
        extract_metadata(imgs_folder)

        log.info(f"request {req_id}: zipping processed images")
        zip_buffer = zip_files(imgs_folder)

        response = (
            send_file(
                zip_buffer,
                as_attachment=True,
                mimetype="application/zip",
                download_name=ZIP_NAME,
            ),
            200,
        )

        response = make_response(response)
        response.headers["X-Request-Id"] = req_id
        response.headers["Access-Control-Expose-Headers"] = "X-Request-Id"
    except LargeZipError as e:
        log.error(f"request {req_id}: zipfile exceeds size limit -> {e}")
        return ERR_ZIP_SIZE_LIMIT
    except InvalidFileError as e:
        log.error(f"request {req_id}: found disallowed file type in zipfile -> {e}")
        return ERR_NON_IMAGE_FILE
    except zipfile.BadZipFile as e:
        log.error(f"request {req_id}: zipfile {file} is corrupted -> {e}")
        return ERR_ZIP_CORRUPT
    except SaveZipFileError as e:
        log.error(f"request {req_id}: failed to save zipfile -> {e}")
        return ERR_SAVE_ZIP
    except UnzipError as e:
        log.error(f"request {req_id}: error occured while unzipping -> {e}")
        return ERR_UNZIP_FILE
    except ZipError as e:
        log.error(f"request {req_id}: error occured while zipping/unzipping -> {e}")
        response = ERR_ZIP_TO_MEMORY
    except ExtractMetaError as e:
        log.error(f"request {req_id}: failed to extract metadata from images -> {e}")
        response = ERR_EXTRACT_META
    finally:
        log.info(f"request {req_id}: cleaning up temp folder")
        shutil.rmtree(base_folder)

    log.info(f"request {req_id}: sending response")
    return response


if __name__ == "__main__":
    app.run(debug=True)
