import json
import tempfile
import zipfile
from pathlib import Path


def get_secrets(mounted_value):
    """A helper method for loading secrets from either a GCF mount point or a local secrets folder.
    json file

    Raises:
        FileNotFoundError: If the secrets file can't be found.

    Returns:
        dict: The secrets .json loaded as a dictionary
    """

    secret_folder = Path("/secrets")

    if mounted_value != "":
        return json.loads(mounted_value)

    #: Otherwise, try to load a local copy for local development
    secret_folder = Path(__file__).parent / "secrets"
    if secret_folder.exists():
        return json.loads((secret_folder / "secrets.json").read_text(encoding="utf-8"))

    raise FileNotFoundError("Secrets folder not found; secrets not loaded.")


class UnzipData:
    def __init__(self, blob):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tempfile = tempfile.NamedTemporaryFile()
        blob.download_to_file(self.tempfile, timeout=300)

        #: unzip this file
        zip_path = Path(self.temp_dir) / "upload.zip"
        Path(self.tempfile.name).rename(zip_path)
        self.zipfile = zipfile.ZipFile(zip_path, "r")

        self.zip_file.extractall(self.temp_dir)
        data_zip = Path(self.temp_dir) / "data.zip"

        self.item_json = json.load(Path(self.temp_dir) / "item.json")
        self.data_json = json.load(Path(self.temp_dir) / "data.json")

        self.data_zip = None
        if data_zip.exists():
            self.data_zip = data_zip

    def __enter__(self):
        return (self.item_json, self.data_json, self.data_zip)

    def __exit__(self):
        self.zip_file.close()
        self.tempfile.close()
        self.temp_dir.cleanup()
