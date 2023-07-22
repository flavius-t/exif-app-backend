import os
import io
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


def create_file_of_size(size_in_mb: int) -> io.BytesIO:
    size_in_bytes = size_in_mb * 1000 * 1000
    in_memory_file = io.BytesIO()
    in_memory_file.write(b"\x00" * size_in_bytes)
    in_memory_file.seek(0)
    return in_memory_file
