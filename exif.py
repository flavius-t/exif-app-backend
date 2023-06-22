import os
import shutil

from flask import Flask, request, send_file
from flask_cors import CORS
from utils.extract_meta import extract_metadata
from utils.zip import unzip_file, zip_files
from utils.constants import UPLOAD_FOLDER, IMAGES_FOLDER, ZIP_NAME


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
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    zip_path = os.path.join(UPLOAD_FOLDER, ZIP_NAME)
    file.save(zip_path)
    unzip_file(zip_path, IMAGES_FOLDER)

    extract_metadata(IMAGES_FOLDER)

    zip_files(zip_path, IMAGES_FOLDER)

    response = send_file(zip_path, as_attachment=True)

    shutil.rmtree(IMAGES_FOLDER)

    return response, 200


if __name__ == '__main__':
    app.run()
