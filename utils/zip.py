import zipfile
import os

# TODO: error handling
def unzip_file(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

# TODO: error handling
def zip_files(output_path, folder_path: str):
    # Ensure folder path is valid
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files and subdirectories
        for root, _, files in os.walk(folder_path):
            for file in files:
                # Get absolute file path
                file_path = os.path.join(root, file)

                # Add file to zip
                zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))
