# Project Moonwalk

Open source ArcGIS Online item backup and restore with style.

Add a `backup` tag to your item and moonwalk will start backing up your items.

This project is split into 2 parts. backup and restore. The backup service scans for items with the `backup` tag and uses the `createReplica` and `data` endpoints to extract the information necessary to restore the item. This data is placed in Google Cloud Storage. Backups are created daily and kept on a rolling 14 day schedule. Every sunday, the backup is also stored in a special area for 90 days.

The restore service consists of a website that allows you to view your backups and trigger a restore.

## Installation

1. Run some terraform to create some cloud infrastructure

## Development

### Jobs

1. `conda create --name moonwalk-backup python=3.11`
1. `conda activate moonwalk-backup`
1. `cd jobs`
1. `pip install -e ".[tests]"`
1. Create `src/backup/secrets/secrets.json` based on `secrets/secrets.example.json`.
1. `backup` - Run the backup job to populate the emulator database and bucket with data. Remember to start the emulators in the root project before running this command.

### Functions

#### Python

The firebase emulator requires that you create a virtual environment. It does not seem to recognize conda environments. Use [pyenv](https://github.com/pyenv/pyenv) if your system python is not 3.11.

1. `cd functions/python`
1. `python -m venv venv`
1. `source venv/bin/activate` (MacOS) `venv\Scripts\Activate.ps1` (Windows Powershell)
1. `pip install -r requirements.txt`

#### Node

1. `cd functions/node`
1. `pnpm install`

Enable versioning on the emulator bucket:

```bash
gcloud storage buckets update gs://ut-dts-agrc-moonwalk-dev.appspot.com --versioning
```

### Dependency Updates

As of 5/20/2025, the `arcgis` python package only supports up through python 3.11. When it adds support for 3.13, the version number will need to be updated in the following locations:

- `.github/actions/deploy-firebase/action.yml`
- `.github/workflows/pull_request.yml`
- `firebase.json`

Firebase already supports 3.13.
