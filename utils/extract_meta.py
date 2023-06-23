import json
import os
import logging
from PIL import ExifTags, Image


log = logging.getLogger(__name__)
logging.getLogger('PIL').setLevel(logging.INFO)


def extract_metadata(folder_path: str):
    '''
    Extracts and removes metadata from all images in a folder.
    '''
    for file in os.listdir(folder_path):
        # TODO: check for other image types or sanitize input
        if file.endswith('.jpg'):
            _extract_metadata(os.path.join(folder_path, file))

def _extract_metadata(file_path: str):
    '''
    Extracts and removes metadata from an image file.
    '''
    log.debug(f'Extracting metadata from {file_path}')

    metadata = {}

    # TODO: modularize
    with Image.open(file_path) as img:
        metadata['format'] = img.format
        metadata['mode'] = img.mode
        metadata['size'] = img.size

        if img._getexif() is not None:
            metadata['exif'] = {
                ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in ExifTags.TAGS
            }

            for k, v in metadata['exif'].items():
                if not isinstance(v, str) and not isinstance(v, int):
                    metadata['exif'][k] = str(v)

            # check if img has info attribute
            if hasattr(img, 'info'):
                _remove_exif(img)

        return _write_to_json(img.filename, metadata)

def _remove_exif(img: Image):
    if "exif" in img.info:
        img.info.pop("exif")
        img.save(img.filename)

def _write_to_json(filename: str, metadata: dict):
    base_name = os.path.splitext(filename)[0]
    output_file_path = f'{base_name}_meta.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(metadata, output_file, indent=4)
 