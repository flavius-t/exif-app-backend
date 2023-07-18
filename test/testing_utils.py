import os
from PIL import Image

def create_text_files(num_files, test_folder):
    for i in range(num_files):
        file_path = os.path.join(test_folder, f"test_file_{i}.txt")
        with open(file_path, "w") as f:
            f.write("testing")


def create_image_files(num_files, test_folder):
    for i in range(num_files):
        file_path = os.path.join(test_folder, f"test_file_{i}.jpg")
        image = Image.new("RGB", (500, 500), "white")
        image.save(file_path, "JPEG")


def create_mixed_files(num_files, test_folder):
    create_text_files(num_files, test_folder)
    create_image_files(num_files, test_folder)
