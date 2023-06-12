from flask import Flask, request


app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'image' not in request.files:
        return 'No file uploaded', 400

    image = request.files['image']

    return 'Image uploaded successfully'


if __name__ == '__main__':
    app.run()
