import json
from pathlib import Path

from google.cloud import storage

# from google.oauth2 import service_account

# CREDENTIAL_FILE = Path("./service-account.json")

# if not CREDENTIAL_FILE.exists():
#     raise FileNotFoundError("missing service account")

# credential_data = {}
# with CREDENTIAL_FILE.open() as reader:
#     credential_data = json.load(reader)

# CREDENTIALS = service_account.Credentials.from_service_account_info(credential_data)

STORAGE_CLIENT = storage.Client()


def get_secrets():
    """A helper method for loading secrets from either a GCF mount point or a local secrets folder.
    json file

    Raises:
        FileNotFoundError: If the secrets file can't be found.

    Returns:
        dict: The secrets .json loaded as a dictionary
    """

    secret_folder = Path("/secrets")

    #: Try to get the secrets from the Cloud Function mount point
    if secret_folder.exists():
        return json.loads(Path("/secrets/app/secrets.json").read_text(encoding="utf-8"))

    #: Otherwise, try to load a local copy for local development
    secret_folder = Path(__file__).parent / "secrets"
    if secret_folder.exists():
        return json.loads((secret_folder / "secrets.json").read_text(encoding="utf-8"))

    raise FileNotFoundError("Secrets folder not found; secrets not loaded.")


def write_to_bucket(bucket, item_id, filename, data, needs_weekly_backup):
    bucket_name = get_secrets()["BUCKET_NAME"]
    bucket = STORAGE_CLIENT.bucket(bucket_name)

    paths = [f"short/{item_id}/{filename}"]

    if needs_weekly_backup:
        paths.append(f"long/{item_id}/{filename}")

    for path in paths:
        blob = bucket.blob(path)
        blob.upload_from_string(json.dumps(data))
