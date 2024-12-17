# project-moonwalk

Open source ArcGIS Online item backup and restore with style.

Add a `backup` tag to your item and moonwalk will start backing up your items.

This project is split into 2 parts. backup and restore. The backup service scans for items with the `backup` tag and uses the `createReplica` and `data` endpoints to extract the information necessary to restore the item. This data is placed in Google Cloud Storage. Backups are created daily and kept on a rolling 14 day schedule. Every sunday, the backup is also stored in a special area for 90 days.

The restore service consists of a website that allows you to view your backups and trigger a restore.

## Installation

1. Run some terraform to create some cloud infrastructure

## Development

### Jobs

1. `conda create --name moonwalk-backup python=3.12`
1. `conda activate moonwalk-backup`
1. `cd jobs`
1. `pip install -e ".[tests]"`
1. `moonwalk-backup` - Run the backup job to populate the emulator database and bucket with data. Remember to start the emulators in the root project before running this command.

### Functions

1. `cd functions`
1. `python -m venv .venv`
1. `pip install -r requirements.txt`

Enable versioning on the emulator bucket:

```bash
gcloud storage buckets update gs://ut-dts-agrc-moonwalk-dev.appspot.com --versioning
```
