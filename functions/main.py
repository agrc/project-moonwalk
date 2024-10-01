import arcgis
from firebase_admin import initialize_app
from firebase_functions import https_fn, options
from firebase_functions.params import SecretParam
from google.cloud import storage

from utilities import UnzipData, get_secrets

try:
    STORAGE_CLIENT = storage.Client()
    UPLOAD_ITEM_TITLE = "moonwalk-restore"

    initialize_app()

    secrets = get_secrets()
    bucket_name = secrets["BUCKET_NAME"]
    bucket = STORAGE_CLIENT.bucket(bucket_name)
except Exception:
    print("failed to initialize firebase app or clients")


def cleanup_restores(gis):
    print("Cleaning up any old restores...")
    items = gis.content.search(query=f"title:{UPLOAD_ITEM_TITLE}")
    for item in items:
        item.delete(permanent=True)


def truncate_and_append(item_id, category, generation, item, gis):
    category_path = f"{category}/{item_id}/upload.zip"
    blob = bucket.blob(category_path, generation=generation)

    with UnzipData(blob) as (_, _, data_zip):
        fgdb_item = upload_fgdb(data_zip, gis)

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


def upload_fgdb(zip_path, gis):
    print("uploading fgdb")
    fgdb_item = gis.content.add(
        item_properties={
            "type": "File Geodatabase",
            "title": UPLOAD_ITEM_TITLE,
            "snippet": "temporary upload from moonwalk",
        },
        data=str(zip_path),
    )

    return fgdb_item


def recreate_item(item_id, category, generation, gis):
    print("Item not found; creating new item...")

    category_path = f"{category}/{item_id}/upload.zip"
    blob = bucket.blob(category_path, generation=generation)

    with UnzipData(blob) as (item_json, _, data_zip):
        fgdb_item = upload_fgdb(data_zip, gis)

        print("publishing")
        #: todo: should we worry about restoring layer ids?
        published_item = fgdb_item.publish(
            publish_parameters={"name": item_json.get("name")},
        )
        success = published_item.reassign_to(
            target_owner=item_json.get("owner"),
            target_folder=item_json.get("ownerFolder"),
        )
        if not success:
            raise Exception("Failed to reassign item")

            #: sharing
        published_item.sharing.sharing_level = item_json.get("access")
        #: todo: group sharing...

        #: todo: refactor this into a separate function and use in truncate_and_append
        print("updating item")
        #: todo: Sam from Esri recommends looking at what properties are sent when you edit an item in AGOL to see what is supported
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
        supported_properties = {k: v for k, v in item_json.items() if k in supported_property_names}
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


SECRETS = SecretParam("secrets")


@https_fn.on_call(memory=options.MemoryOption.MB_512, secrets=[SECRETS])
def restore(request: https_fn.CallableRequest) -> str:
    print("begin request")
    item_id = request.data.get("item_id")
    category = request.data.get("category")
    generation = request.data.get("generation")
    print(",".join(request.data.keys()))

    if not item_id or not category or not generation:
        raise https_fn.HttpsError("invalid-argument", "Missing required arguments")

    print("logging into AGOL")
    gis = arcgis.gis.GIS(
        url=secrets["AGOL_ORG"],
        username=secrets["AGOL_USER"],
        password=secrets["AGOL_PASSWORD"],
    )
    cleanup_restores(gis)

    print(f"Restoring {item_id} from {category} ({generation})...")

    item_exists = True
    try:
        item = arcgis.gis.Item(gis, item_id)
    except Exception:
        item_exists = False

    if item_exists:
        if item.type == arcgis.gis.ItemTypeEnum.FEATURE_SERVICE.value:
            truncate_and_append(item_id, category, generation, item, gis)

            return "Item restored successfully via truncate and append"
        else:
            raise https_fn.HttpsError("invalid-argument", f"Unsupported item type: {item.type}")
            #: this breaks web maps and experience builder projects, not sure why
            # print(f"overwriting item: {item_id} from {category}")
            # success = item.update(
            #     item_properties=json.loads(
            #         Path(f"./temp/sample-bucket/{item_id}/{category}/item.json").read_text(encoding="utf-8")
            #     ),
            #     data=str(Path(f"./temp/sample-bucket/{item_id}/{category}/data.json")),
            # )
            # if not success:
            #     print("Failed to update item")
            #     return
    else:
        new_id = recreate_item(item_id, category, generation, gis)

        return f"Item restored successfully via recreation. New Item ID: {new_id}"
