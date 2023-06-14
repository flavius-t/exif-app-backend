import zipfile
import os

UPLOAD_FOLDER = 'temp'
IMAGES_FOLDER = f'{UPLOAD_FOLDER}/images'



def unzip_file(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def make_temp_dirs():
    # creates /temp/images folder (including /temp folder)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
