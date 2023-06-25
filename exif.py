import io
import os
import shutil
import uuid
import logging

from flask import Flask, request, send_file
from flask_cors import CORS
from utils.extract_meta import extract_metadata
from utils.zip import unzip_file, zip_files
from utils.constants import UPLOAD_FOLDER, ZIP_NAME


app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


ERR_NO_FILES = 'No files contained in request', 400
ERR_NO_ZIP = 'Request is missing zipfile', 400
ERR_TEMP_FOLDER = 'Internal error occured while processing images: failed to create temp folder', 500
ERR_NON_IMAGE_FILE = 'Non-image file detected in upload', 400
ERR_READ_INTO_MEMORY = 'Internal error occured while processing images: failed to read zipfile into memory', 500


def save_zipfile(file, folder: str):
    zip_path = os.path.join(folder, ZIP_NAME)
    file.save(zip_path)
    file.close()
    return zip_path


def create_temp_folder(req_id: str):
    base_folder = f'{UPLOAD_FOLDER}/{req_id}'
    imgs_folder = f'{base_folder}/images'
    try:
        os.makedirs(imgs_folder)
    except OSError as e:
        log.error(f'request {req_id}: could not create folder {imgs_folder} -- folder already exists')
        raise e
    
    return base_folder, imgs_folder


def read_into_memory(filepath: str) -> io.BytesIO:
    return_data = io.BytesIO()
    with open(filepath, 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)

    return return_data


@app.route('/upload', methods=['POST'])
def handle_upload():
    req_id = str(uuid.uuid4())
    log.info(f'Received new upload, assigning request_id {req_id}')

    if not request.files:
        log.error(f'request {req_id}: no files uploaded')
        return ERR_NO_FILES

    if 'file' not in request.files:
        log.error(f'request {req_id}: zipfile is missing from request.files')
        return ERR_NO_ZIP

    file = request.files['file']

    # TODO: validate and sanitize zipfile contents before saving

    log.info(f'request {req_id}: creating temp folder')
    try:
        base_folder, imgs_folder = create_temp_folder(req_id)
    except OSError:
        return ERR_TEMP_FOLDER

    try:
        log.info(f'request {req_id}: saving zipfile to temp folder')
        zip_path = save_zipfile(file, base_folder)

        log.info(f'request {req_id}: unzipping images')
        unzip_file(zip_path, imgs_folder)

        log.info(f'request {req_id}: extracting image metadata')
        extract_metadata(imgs_folder)

        log.info(f'request {req_id}: zipping processed images')
        # TODO: error handling
        zip_files(zip_path, imgs_folder)

        log.info(f'request {req_id}: reading zipfile into memory for response')
        # needed to allow deletion of temp folder containing zipfile
        return_data = read_into_memory(zip_path)

        response = send_file(return_data, as_attachment=True, mimetype="application/zip", download_name="images.zip"), 200
    except ValueError as e:
        log.error(f'request {req_id}: found non-image file -> {e}')
        response = ERR_NON_IMAGE_FILE
    except OSError as e:
        log.error(f'request {req_id}: could not read zipfile into memory -> {e}')
        response = ERR_READ_INTO_MEMORY
    finally:
        log.info(f'request {req_id}: cleaning up temp folder')
        shutil.rmtree(base_folder)

    log.info(f'request {req_id}: sending response')
    return response


if __name__ == '__main__':
    app.run(debug=True)
