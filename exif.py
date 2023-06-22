import io
import os
import shutil
import uuid

from flask import Flask, request, send_file
from flask_cors import CORS
from utils.extract_meta import extract_metadata
from utils.zip import unzip_file, zip_files
from utils.constants import UPLOAD_FOLDER, ZIP_NAME


app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def handle_upload():
    if not request.files:
        return 'No files uploaded', 400

    if 'file' not in request.files:
        return 'Request is missing zipfile', 400

    file = request.files['file']

    # save images to temp folder
    base_folder = f'{UPLOAD_FOLDER}/{str(uuid.uuid4())}'
    imgs_folder = f'{base_folder}/images'
    os.makedirs(imgs_folder) # TODO: handle already exists error
    zip_path = os.path.join(base_folder, ZIP_NAME)
    file.save(zip_path)
    file.close()
    unzip_file(zip_path, imgs_folder)

    extract_metadata(imgs_folder)

    zip_files(zip_path, imgs_folder)

    # TODO: error handling
    return_data = io.BytesIO()
    with open(zip_path, 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)

    shutil.rmtree(base_folder)

    return send_file(return_data, as_attachment=True, mimetype="application/zip", download_name="images.zip"), 200


if __name__ == '__main__':
    app.run()
