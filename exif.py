from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def handle_upload():
    if not request.files:
        return 'No files uploaded', 400

    for key, file in request.files.items():
        # TODO: process files, check file type, etc.
        print(key, file)

    # TODO: respond with processed files
    return 'Images uploaded successfully', 200


if __name__ == '__main__':
    app.run()
