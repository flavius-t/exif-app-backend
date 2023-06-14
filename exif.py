from flask import Flask, request
from flask_cors import CORS
import os
from utils.extract_meta import extract_metadata, remove_exif
from utils.zip import unzip_file, make_temp_dirs, UPLOAD_FOLDER, IMAGES_FOLDER


app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def handle_upload():
    if not request.files:
        return 'No files uploaded', 400
    
    if 'file' not in request.files:
        return 'Request is missing zipfile', 400
    
    file = request.files['file']

    make_temp_dirs()
    zip_path = os.path.join(UPLOAD_FOLDER, 'images.zip')
    file.save(zip_path)
    unzip_file(zip_path, IMAGES_FOLDER)

    response = {}
    print(response)

    # TODO: respond with processed files
    return response, 200


if __name__ == '__main__':
    app.run()
