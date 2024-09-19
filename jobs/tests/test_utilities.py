#!/usr/bin/env python
# * coding: utf8 *
"""
test_utilities.py
A module that contains tests for the project module.
"""

import tempfile
from pathlib import Path
from zipfile import ZipFile

from backup import utilities


def test_add_to_zip():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Path for the temporary zip file
        zip_path = temp_dir_path / "test.zip"

        # Call the function to add the file to the zip
        utilities.add_to_zip(zip_path, [("test_file.txt", "This is a test file.")])

        # Verify that the file was added to the zip
        with ZipFile(zip_path, "r") as zip_file:
            assert "test_file.txt" in zip_file.namelist()

            with zip_file.open("test_file.txt") as file_in_zip:
                content = file_in_zip.read().decode("utf-8")

                assert content == "This is a test file."
