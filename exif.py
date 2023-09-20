"""
Flask app for uploading zip files containing images, extracting metadata from the images, and returning a zip file
"""

import shutil
import uuid
import logging
import zipfile
import os
import datetime
from io import BytesIO

from dotenv import load_dotenv
from flask import Flask, request, send_file, make_response, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies,
)

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
    CreateTempFolderError,
    SaveZipFileError,
    ZIP_SIZE_LIMIT_MB,
)
from utils.mongo_utils import (
    create_mongo_client,
    create_db,
    create_collection,
    close_connection,
    add_user,
    get_user,
)
from utils.file_permissions import restrict_file_permissions
from models.users import User, USERNAME_FIELD, PASSWORD_FIELD


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


# Flask app and api setup
app = Flask(__name__)
ACCEPT_ORIGINS = ["http://localhost:3000"]
CORS(app, origins=ACCEPT_ORIGINS, supports_credentials=True)


FLASK_ENV = os.getenv("FLASK_ENV")
if FLASK_ENV == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")


# MongoDB setup
DB_NAME = app.config["DB_NAME"]
USERS_COLLECTION = app.config["USERS_COLLECTION"]
mongo_client = create_mongo_client(MONGO_URI)
db = create_db(mongo_client, DB_NAME)
users = create_collection(db, USERS_COLLECTION)

# JWT setup
app.config["JWT_COOKIE_SECURE"] = False  # TODO: set True for production
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.secret_key = os.getenv("FLASK_SECRET_KEY")
JWT_EXPIRES_MINS = app.config["JWT_EXPIRATION_DELTA_MINS"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=JWT_EXPIRES_MINS)
app.config["JWT_COOKIE_REFRESH_WINDOW"] = app.config[
    "JWT_REFRESH_WINDOW_MINS"
]  # issues a new cookie if the user is within 15 minutes of expiry
jwt = JWTManager(app)


# logging setup
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


# generic endpoint responses
ERR_NO_JSON = "Request contains no json", 400


# /upload endpoint responses
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


@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Returns the current user's profile.
    """
    user_id = get_jwt_identity()
    return jsonify(message=f"Hello, {user_id}!"), 200


@app.route("/upload", methods=["POST"])
@jwt_required()
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
    except CreateTempFolderError as e:
        log.error(f"request {req_id}: could not create temp folder -> {e}")
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

        log.info(f"request {req_id}: restricting execute permissions")
        restrict_file_permissions(imgs_folder)

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


ERR_MISSING_CREDENTIALS = "Missing username or password", 400
ERR_USER_NOT_EXIST = "User does not exist", 400
ERR_WRONG_PASSWORD = "Wrong password", 400
ERR_CREATE_JWT = "JWT creation failed", 500
ERR_USER_EXISTS = "User already exists", 409
ERR_CREATE_USER = "Failed to create new user", 500

REGISTER_SUCCESS = "User registration successful", 201
LOGIN_SUCCESS = "User login successful", 200
LOGOUT_SUCCESS = "User logout successful", 200


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get(USERNAME_FIELD)
        password = data.get(PASSWORD_FIELD)

        if username is None or password is None:
            return jsonify(message=ERR_MISSING_CREDENTIALS[0]), ERR_MISSING_CREDENTIALS[1]

        user = get_user(users, username)

        if not user:
            return jsonify(message=ERR_USER_NOT_EXIST[0]), ERR_USER_NOT_EXIST[1]

        if user[PASSWORD_FIELD] == password:
            try:
                response = jsonify(message=LOGIN_SUCCESS[0])
                access_token = create_access_token(identity=user[USERNAME_FIELD])
                set_access_cookies(response, access_token)
                return response, LOGIN_SUCCESS[1]
            except Exception:
                return jsonify(message=ERR_CREATE_JWT[0]), ERR_CREATE_JWT[1]
        else:
            return jsonify(message=ERR_WRONG_PASSWORD[0]), ERR_WRONG_PASSWORD[1]


@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        username = data.get(USERNAME_FIELD)
        password = data.get(PASSWORD_FIELD)

        if username is None or password is None:
            return jsonify(message=ERR_MISSING_CREDENTIALS[0]), ERR_MISSING_CREDENTIALS[1]

        if get_user(users, username):
            return jsonify(message=ERR_USER_EXISTS[0]), ERR_USER_EXISTS[1]

        try:
            # TODO: hash password first
            user = User(username=username, password=password)
            add_user(users, user.username, user.password)
        except Exception:
            return jsonify(message=ERR_CREATE_USER[0]), ERR_CREATE_USER[1]

        return jsonify(message=REGISTER_SUCCESS[0]), REGISTER_SUCCESS[1]


@app.route("/logout", methods=["GET"])
def logout():
    response = jsonify(message=LOGOUT_SUCCESS[0])
    unset_jwt_cookies(response)
    return response, LOGOUT_SUCCESS[1]


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now()
        target_timestamp = datetime.datetime.timestamp(
            now + datetime.timedelta(minutes=app.config["JWT_COOKIE_REFRESH_WINDOW"])
        )
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # not a valid JWT
        return response


@app.teardown_appcontext
def clean_up_resources(exception):
    if isinstance(exception, KeyboardInterrupt):
        close_connection(mongo_client)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
