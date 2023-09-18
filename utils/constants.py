"""
Constants used by the application.
"""

# path to folder containing temporary folders for image processing
UPLOAD_FOLDER = "temp"

# name of zip file returned by /upload endpoint
ZIP_NAME = "images.zip"

# file extensions accepted by /upload endpoint
ALLOWED_EXTENSIONS = set(["jpg", "jpeg", "png"])

# maximum size of zip file accepted by /upload endpoint in MB
ZIP_SIZE_LIMIT_MB = 100
