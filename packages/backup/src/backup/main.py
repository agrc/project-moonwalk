import json
from datetime import datetime
from pathlib import Path
from pprint import pprint

import arcgis
from utilities import delete_folder, write_to_bucket

NEEDS_WEEKLY_BACKUP = datetime.today().weekday() == 0
EXPORT_FILENAME = "moonwalk-export.zip"


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


def cleanup_exports(gis):
    print("Cleaning up any old exports...")
    items = gis.content.search(query=f"title:{EXPORT_FILENAME}")
    for item in items:
        item.delete(permanent=True)


def backup():
    secrets = _get_secrets()
    gis = arcgis.GIS(
        url=secrets["AGOL_ORG"],
        username=secrets["AGOL_USER"],
        password=secrets["AGOL_PASSWORD"],
    )

    cleanup_exports(gis)

    page_size = 100
    has_more = True
    start = 1
    summary = {}
    supported_types = [
        arcgis.gis.ItemTypeEnum.FEATURE_SERVICE.value,
        arcgis.gis.ItemTypeEnum.WEB_EXPERIENCE.value,
        arcgis.gis.ItemTypeEnum.WEB_MAP.value,
        arcgis.gis.ItemTypeEnum.WEB_SCENE.value,
        arcgis.gis.ItemTypeEnum.WEB_MAPPING_APPLICATION.value,
    ]

    while has_more:
        response = gis.content.advanced_search(
            query=f"orgid:{gis.properties.id}",
            filter=f'tags:{secrets["TAG_NAME"]}',
            max_items=page_size,
            start=start,
        )

        #: couldn't query or filter multiple types at once, so filtering here
        for item in [filteredItem for filteredItem in response["results"] if filteredItem.type in supported_types]:
            print(f"Preparing {item.title} ({item.type}, {item.id})")
            item_json = dict(item)

            versions = write_to_bucket("sample-bucket", item.id, "item.json", item_json, NEEDS_WEEKLY_BACKUP)
            versions = write_to_bucket("sample-bucket", item.id, "data.json", item.get_data(), NEEDS_WEEKLY_BACKUP)

            summary[item.id] = {
                "title": item.title,
                "versions": versions,
                "type": item.type,
            }

            if item.type == arcgis.gis.ItemTypeEnum.FEATURE_SERVICE.value:
                try:
                    print("Requesting feature service export")
                    export_item = item.export(
                        EXPORT_FILENAME,
                        arcgis.gis.ItemTypeEnum.FILE_GEODATABASE.value,
                        #: This could be set to false and then we could download later. We tried this and the problem was that we could not find a reliable way to know if the export was complete.
                        wait=True,
                        tags=[],
                    )

                    print("Downloading exported item...")
                    export_item.download(save_path=f"./temp/sample-bucket/{item.id}", file_name="data.zip")
                except Exception as error:
                    print(error)
                    print(
                        f"Failed to export and download {export_item.title} ({export_item.id}), {export_item.status()}"
                    )
                export_item.delete(permanent=True)

        has_more = response["nextStart"] > 0
        start = response["nextStart"]

    pprint(summary)


def local_backup():
    temp_folder = Path("./temp")
    delete_folder(temp_folder)
    backup()


if __name__ == "__main__":
    local_backup()
