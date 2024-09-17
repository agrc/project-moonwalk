import json
from datetime import datetime
from pathlib import Path
from pprint import pprint
from time import sleep

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
    export_jobs = []
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
                print("Requesting feature service export")

                job = item.export(
                    "moonwalk-export.zip",
                    arcgis.gis.ItemTypeEnum.FILE_GEODATABASE.value,
                    wait=False,
                    tags=[],
                )
                export_jobs.append(job)

        has_more = response["nextStart"] > 0
        start = response["nextStart"]

    print("Downloading export jobs")

    while len(export_jobs) > 0:
        for job in export_jobs:
            item = arcgis.gis.Item(gis, job["exportItemId"])

            try:
                item.download(save_path=f'./temp/sample-bucket/{job["serviceItemId"]}', file_name="data.zip")
                job["downloaded"] = True
                item.delete(permanent=True)
            except Exception as error:
                print(error)
                print(f"Failed to download {item.title} ({item.id}), {item.status()}")

        export_jobs = [job for job in export_jobs if "downloaded" not in job]

        if len(export_jobs) > 0:
            print("waiting 5 seconds...", len(export_jobs))
            sleep(5)

    pprint(summary, indent=2)


def local_backup():
    temp_folder = Path("./temp")
    delete_folder(temp_folder)
    backup()


if __name__ == "__main__":
    local_backup()
