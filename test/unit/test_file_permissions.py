import pytest
import os
import shutil

from utils.file_permissions import restrict_file_permissions
from test.testing_utils import create_mixed_files


TEST_FOLDER = os.path.join("test", "unit", "test_file_perm")


def test_restrict_file_permissions():
    """
    Tests that restrict_folder_permissions() sets the correct permissions on a folder.
    """
    os.mkdir(TEST_FOLDER)
    create_mixed_files(2, TEST_FOLDER)
    try:
        restrict_file_permissions(TEST_FOLDER)
        for file in os.listdir(TEST_FOLDER):
            file_path = os.path.join(TEST_FOLDER, file)
            assert oct(os.stat(file_path).st_mode)[-3:] == "644"
    finally:
        shutil.rmtree(TEST_FOLDER)
        pass
