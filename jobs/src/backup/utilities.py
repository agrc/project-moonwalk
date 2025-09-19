import json
from os import getenv
from pathlib import Path
from zipfile import ZipFile

from arcgis.features import FeatureLayerCollection
from google.cloud import firestore, storage

if not getenv("CI"):
    STORAGE_CLIENT = storage.Client()
    project = None
    if getenv("FIRESTORE_EMULATOR_HOST"):
        project = "ut-dts-agrc-moonwalk-dev"
    FIRESTORE_CLIENT = firestore.Client(project)


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


def write_to_bucket(item_id, filename, path, needs_weekly_backup, row_counts: dict | None = None):
    bucket_name = get_secrets()["BUCKET_NAME"]
    bucket = STORAGE_CLIENT.bucket(bucket_name)

    category_path = f"short/{item_id}/{filename}"

    if needs_weekly_backup:
        category_path = f"long/{item_id}/{filename}"

    blob = bucket.blob(category_path)

    if row_counts:
        # Convert row_counts to string metadata (GCS metadata values must be strings)
        metadata = {
            "row_counts": json.dumps(row_counts),
        }
        blob.metadata = metadata

    blob.upload_from_filename(path)


def get_versions(item_id: str):
    bucket_name = get_secrets()["BUCKET_NAME"]
    bucket = STORAGE_CLIENT.bucket(bucket_name)

    short_blobs = bucket.list_blobs(prefix=f"short/{item_id}/backup.zip", versions=True)
    long_blobs = bucket.list_blobs(prefix=f"long/{item_id}/backup.zip", versions=True)
    all_blobs = list(short_blobs) + list(long_blobs)

    versions = []

    for blob in all_blobs:
        data = {
            "category": Path(blob.name).parts[0],
            "generation": blob.generation,
            "updated": blob.updated,
        }
        if blob.metadata and "row_counts" in blob.metadata:
            try:
                # Parse the JSON string back to a dictionary
                parsed_row_counts = json.loads(blob.metadata["row_counts"])
                data["rowCounts"] = parsed_row_counts
            except (json.JSONDecodeError, KeyError):
                pass  # If parsing fails, just don't add rowCounts
        versions.append(data)

    versions.sort(key=lambda x: x["updated"], reverse=True)

    return versions


def write_to_firestore(item_id: str, item_name: str, date: str, item_type: str) -> dict:
    print("writing to firestore")
    ref = FIRESTORE_CLIENT.collection("items").document(item_id)
    data = {
        "name": item_name,
        "lastBackup": date,
        "versions": get_versions(item_id),
        "itemType": item_type,
    }

    ref.set(data)

    return data


def add_to_zip(zip, items):
    with ZipFile(zip, "w") as zipped_file:
        for name, data in items:
            if data is None:
                continue
            if isinstance(data, Path):
                zipped_file.write(data, name)
            else:
                zipped_file.writestr(name, data)


def ensure_export_ready(fs_item):
    """Ensure a hosted feature service item can be exported."""

    manager = FeatureLayerCollection.fromitem(fs_item).manager
    if "Extract" not in manager.properties.capabilities:
        print("Adding Extract capability")
        manager.properties.capabilities += ",Extract"
        manager.update_definition({"capabilities": manager.properties.capabilities})
