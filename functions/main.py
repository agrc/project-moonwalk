import json
from pathlib import Path

import arcgis
from firebase_admin import initialize_app
from firebase_functions import https_fn

UPLOAD_ITEM_TITLE = "moonwalk-restore"

initialize_app()


def _get_secrets():
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


def cleanup_restores(gis):
    print("Cleaning up any old restores...")
    items = gis.content.search(query=f"title:{UPLOAD_ITEM_TITLE}")
    for item in items:
        item.delete(permanent=True)


def truncate_and_append(item_id, sub_folder, gis, item):
    fgdb_item = upload_fgdb(item_id, sub_folder, gis)

    collection = arcgis.features.FeatureLayerCollection.fromitem(item)

    for layer in collection.layers:
        print(f"truncating layer: {layer.properties.name}")
        layer.manager.truncate(asynchronous=True, wait=True)
        print("appending")
        layer.append(
            item_id=fgdb_item.id,
            upload_format="filegdb",
            source_table_name=layer.properties.name,
            return_messages=True,
            rollback=True,
        )

    for table in collection.tables:
        print(f"truncating table: {table.properties.name}")
        table.manager.truncate(asynchronous=True, wait=True)
        print("appending")
        table.append(
            item_id=fgdb_item.id,
            upload_format="filegdb",
            source_table_name=table.properties.name,
            return_messages=True,
            rollback=True,
        )

    fgdb_item.delete(permanent=True)


def upload_fgdb(item_id, sub_folder, gis):
    print("uploading fgdb")
    zip_path = Path(f"./temp/sample-bucket/{sub_folder}/{item_id}/data.zip")
    fgdb_item = gis.content.add(
        item_properties={
            "type": "File Geodatabase",
            "title": UPLOAD_ITEM_TITLE,
            "snippet": "temporary upload from moonwalk",
        },
        data=str(zip_path),
    )

    return fgdb_item


def recreate_item(item_id, sub_folder, gis):
    print("Item not found; creating new item...")

    fgdb_item = upload_fgdb(item_id, sub_folder, gis)

    original_item_properties = json.loads(
        Path(f"./temp/sample-bucket/{sub_folder}/{item_id}/item.json").read_text(encoding="utf-8")
    )

    print("publishing")
    #: todo: should we worry about restoring layer ids?
    published_item = fgdb_item.publish(
        publish_parameters={"name": original_item_properties.get("name")},
    )
    success = published_item.reassign_to(
        target_owner=original_item_properties.get("owner"),
        target_folder=original_item_properties.get("ownerFolder"),
    )
    if not success:
        raise Exception("Failed to reassign item")

        #: sharing
    published_item.sharing.sharing_level = original_item_properties.get("access")
    #: todo: group sharing...

    print("updating item")
    supported_property_names = [
        "description",
        "title",
        "tags",
        "snippet",
        "extent",
        "accessInformation",
        "licenseInfo",
        "culture",
        "access",
    ]
    supported_properties = {k: v for k, v in original_item_properties.items() if k in supported_property_names}
    success = published_item.update(
        item_properties=supported_properties,
    )
    #: metadata?

    print("deleting fgdb")
    #: get a new item reference since the owner has changed
    gis.content.get(fgdb_item.id).delete(permanent=True)

    if not success:
        raise Exception("Failed to update item")

    print(f"new item created: {published_item.id}")

    return published_item.id


@https_fn.on_request()
def restore(request: https_fn.Request) -> https_fn.Response:
    item_id = request.args.get("item_id")
    sub_folder = request.args.get("sub_folder")

    if not item_id or not sub_folder:
        return https_fn.Response("Missing required parameters", status=400)

    secrets = _get_secrets()
    gis = arcgis.GIS(
        url=secrets["AGOL_ORG"],
        username=secrets["AGOL_USER"],
        password=secrets["AGOL_PASSWORD"],
    )

    cleanup_restores(gis)

    print(f"Restoring {item_id} from {sub_folder}...")

    item_exists = True
    try:
        item = arcgis.gis.Item(gis, item_id)
    except Exception:
        item_exists = False

    if item_exists:
        if item.type == arcgis.gis.ItemTypeEnum.FEATURE_SERVICE.value:
            truncate_and_append(item_id, sub_folder, gis, item)

            return https_fn.Response("Item restored successfully via truncate and append")
        else:
            raise NotImplementedError(f"Unsupported item type: {item.type}")
            #: this breaks web maps and experience builder projects, not sure why
            # print(f"overwriting item: {item_id} from {sub_folder}")
            # success = item.update(
            #     item_properties=json.loads(
            #         Path(f"./temp/sample-bucket/{item_id}/{sub_folder}/item.json").read_text(encoding="utf-8")
            #     ),
            #     data=str(Path(f"./temp/sample-bucket/{item_id}/{sub_folder}/data.json")),
            # )
            # if not success:
            #     print("Failed to update item")
            #     return
    else:
        new_id = recreate_item(item_id, sub_folder, gis)

        return https_fn.Response(f"Item restored successfully via recreation. New Item ID: {new_id}")
