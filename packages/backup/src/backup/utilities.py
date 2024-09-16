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
BUCKET_NAME = "ut-dts-agrc-moonwalk-dev"

def write_to_gcs(bucket_name, folder, filename, data, needs_weekly_backup):
    bucket = STORAGE_CLIENT.bucket(bucket_name)

    paths = [folder / 'short' / filename]

    if needs_weekly_backup:
        paths.append(folder / "long" / filename)

    for path in paths:
        try:
            blob = bucket.bucket.blob(path)
            blob.upload_from_filename(data)
        except Exception as error:
            print(error)

def write_to_bucket(bucket, folder, filename, data, needs_weekly_backup):
    base_path = Path(f"./temp/{bucket}/{folder}")
    paths = [base_path / 'short' / filename]

    if needs_weekly_backup:
        paths.append(base_path / 'long' / filename)

    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f)

def delete_folder(pth):
    if not pth.exists():
        return

    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder(sub)
        else:
            sub.unlink()
    pth.rmdir()
