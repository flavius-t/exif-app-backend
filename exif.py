from flask import Flask, request
from flask_cors import CORS
import os
from utils.extract_meta import extract_metadata, remove_exif
from utils.zip import unzip_file



app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def handle_upload():
    if not request.files:
        return 'No files uploaded', 400
    
    if 'file' not in request.files:
        return 'Request is missing zipfile', 400
    
    # TODO: modularize all of this
    file = request.files['file']
    upload_folder = 'temp'
    os.makedirs(upload_folder, exist_ok=True)
    zip_path = os.path.join(upload_folder, 'images.zip')
    file.save(zip_path)

    imgs_folder = 'temp/images'
    os.makedirs('temp/images', exist_ok=True)
    unzip_file(zip_path, imgs_folder)

    response = {}
    print(response)

    # TODO: respond with processed files
    return response, 200


if __name__ == '__main__':
    app.run()
