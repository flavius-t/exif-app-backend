"""
Constants used by the application.
"""

# path to folder containing temporary folders for image processing
UPLOAD_FOLDER = "temp"

# name of zip file returned by /upload endpoint
ZIP_NAME = "images.zip"

# file extensions accepted by /upload endpoint
ALLOWED_EXTENSIONS = set(["jpg", "jpeg", "png"])
