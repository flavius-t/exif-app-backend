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


@app.route('/upload', methods=['POST'])
def handle_upload():
    req_id = str(uuid.uuid4())
    log.info(f'Received new upload, request_id = {req_id}')

    if not request.files:
        log.error(f'request {req_id}: no files uploaded')
        return 'No files uploaded', 400

    if 'file' not in request.files:
        log.error(f'request {req_id}: zipfile is missing from request.files')
        return 'Request is missing zipfile', 400

    file = request.files['file']

    # TODO: validate and sanitize zipfile contents before saving

    log.info(f'request {req_id}: saving zipfile to temp folder')
    base_folder = f'{UPLOAD_FOLDER}/{req_id}'
    imgs_folder = f'{base_folder}/images'
    os.makedirs(imgs_folder) # TODO: handle already exists error
    zip_path = os.path.join(base_folder, ZIP_NAME)
    file.save(zip_path)
    file.close()

    log.info(f'request {req_id}: unzipping images')
    unzip_file(zip_path, imgs_folder)

    log.info(f'request {req_id}: extracting image metadata')
    try:
        extract_metadata(imgs_folder)

        log.info(f'request {req_id}: zipping processed images')
        # TODO: error handling
        zip_files(zip_path, imgs_folder)

        # TODO: error handling
        log.info(f'request {req_id}: preparing response')
        return_data = io.BytesIO()
        with open(zip_path, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)

        response = send_file(return_data, as_attachment=True, mimetype="application/zip", download_name="images.zip"), 200
    except ValueError as e:
        log.error(f'request {req_id}: error occured {e}')
        response = "Non-image file detected in upload", 400
    finally:
        log.info(f'request {req_id}: cleaning up temp folder')
        shutil.rmtree(base_folder)

    log.info(f'request {req_id}: sending response')
    return response


if __name__ == '__main__':
    app.run(debug=True)
