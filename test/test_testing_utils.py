import pytest

from test.testing_utils import create_file_of_size

@pytest.mark.parametrize("file_size", [(1), (2), (10), (56), (99), (100)])
def test_create_file_of_size(file_size):
    """
    Tests that create_file_of_size correctly creates a file of the correct size.
    """
    file = create_file_of_size(file_size)
    assert file.getbuffer().nbytes / 1000000 == file_size
    file.close()
