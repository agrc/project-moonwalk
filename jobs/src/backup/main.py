from datetime import datetime
from os import getenv
from pprint import pprint

import arcgis
from dotenv import load_dotenv

load_dotenv()

from utilities import get_secrets, write_to_bucket, write_to_firestore  # noqa: E402

NEEDS_WEEKLY_BACKUP = datetime.today().weekday() == 0
# NEEDS_WEEKLY_BACKUP = True
EXPORT_FILENAME = "moonwalk-export.zip"


def cleanup_exports(gis):
    print("Cleaning up any old exports...")
    items = gis.content.search(query=f"title:{EXPORT_FILENAME}")
    for item in items:
        item.delete(permanent=True)


def backup():
    secrets = get_secrets()

    gis = arcgis.GIS(
        url=getenv("AGOL_ORG"),
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
        # restoring some of these types below just broken them. Perhaps these can be implemented in the future...
        # arcgis.gis.ItemTypeEnum.WEB_EXPERIENCE.value,
        # arcgis.gis.ItemTypeEnum.WEB_MAP.value,
        # arcgis.gis.ItemTypeEnum.WEB_SCENE.value,
        # arcgis.gis.ItemTypeEnum.WEB_MAPPING_APPLICATION.value,
    ]

    while has_more:
        response = gis.content.advanced_search(
            query=f"orgid:{gis.properties.id}",
            filter=f'tags:{getenv("TAG_NAME")}',
            max_items=page_size,
            start=start,
        )

        for item in response["results"]:
            #: we couldn't query or filter multiple types at once, so filtering here
            if item.type not in supported_types:
                print(f"Unsupported item type, skipping: {item.title} ({item.type}, {item.id})")
                continue

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
                    export_item.download(save_path=f"./temp/sample-bucket/short/{item.id}", file_name="data.zip")

                    write_to_firestore(item.id, item.title, datetime.now().isoformat())
                except Exception as error:
                    print(error)
                    print(
                        f"Failed to export and download {export_item.title} ({export_item.id}), {export_item.status()}"
                    )
                export_item.delete(permanent=True)

        has_more = response["nextStart"] > 0
        start = response["nextStart"]

    pprint(summary)


if __name__ == "__main__":
    backup()
