import json
import tempfile
from datetime import datetime, timezone
from os import getenv
from pathlib import Path
from pprint import pprint

from arcgis.gis import GIS, ItemTypeEnum
from dotenv import load_dotenv

"""
Environment Variables (defined locally in .env and set in Github Actions for the cloud projects):
TAG_NAME: The tag to filter items to back up.
AGOL_ORG: The URL of the ArcGIS Online organization to back up.
ENVIRONMENT: Determines the environment (DEV, STAGING, or PROD)

FIRESTORE_EMULATOR_HOST and STORAGE_EMULATOR_HOST are set in .env for local development only.
"""

load_dotenv()

try:
    from .utilities import (  # noqa: E402
        add_to_zip,
        ensure_export_ready,
        get_secrets,
        write_to_bucket,
        write_to_firestore,
    )
except ImportError:
    from utilities import (  # type: ignore
        add_to_zip,  # noqa: E402
        ensure_export_ready,
        get_secrets,
        write_to_bucket,
        write_to_firestore,
    )

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

    gis = GIS(
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
        ItemTypeEnum.FEATURE_SERVICE.value,
        # restoring some of these types below just broken them.
        ItemTypeEnum.WEB_EXPERIENCE.value,
        ItemTypeEnum.WEB_MAP.value,
        ItemTypeEnum.WEB_SCENE.value,
        ItemTypeEnum.WEB_MAPPING_APPLICATION.value,
    ]

    while has_more:
        tag = getenv("TAG_NAME")
        if getenv("ENVIRONMENT") in ["DEV", "STAGING"]:
            tag = "test-backup"
        response = gis.content.advanced_search(
            query=f"orgid:{gis.properties.id}",
            filter=f"tags:{tag}",
            max_items=page_size,
            start=start,
        )

        for item in response["results"]:
            #: we couldn't query or filter multiple types at once, so filtering here
            if item.type not in supported_types:
                print(f"Unsupported item type, skipping: {item.title} ({item.type}, {item.id})")
                continue

            print(f"Preparing {item.title} ({item.type}, {item.id})")
            zip_filename = "backup.zip"
            if item.type == ItemTypeEnum.FEATURE_SERVICE.value:
                try:
                    ensure_export_ready(item)

                    print("Requesting feature service export")
                    export_item = item.export(
                        EXPORT_FILENAME,
                        ItemTypeEnum.FILE_GEODATABASE.value,
                        #: This could be set to false and then we could download later. We tried this and the problem was that we could not find a reliable way to know if the export was complete.
                        wait=True,
                        tags=[],
                    )
                    print("Downloading exported item...")
                    download_path = export_item.download(file_name=zip_filename)
                    export_item.delete(permanent=True)
                except Exception as error:
                    print(f"Export failed for {item.title} ({item.id}): {error}")
                    continue
            else:
                #: create empty zip file in a temporary directory
                download_path = Path(tempfile.gettempdir()) / zip_filename
                download_path.touch()

            item_json = dict(item)
            add_to_zip(
                download_path, [("item.json", json.dumps(item_json)), ("data.json", json.dumps(item.get_data()))]
            )

            write_to_bucket(item.id, zip_filename, download_path, NEEDS_WEEKLY_BACKUP)

            #: cleanup
            Path(download_path).unlink()

            summary[item.id] = write_to_firestore(item.id, item.title, datetime.now(timezone.utc).isoformat())

        has_more = response["nextStart"] > 0
        start = response["nextStart"]

    pprint(summary)


if __name__ == "__main__":
    backup()
