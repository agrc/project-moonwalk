# Copilot Coding Agent Onboarding Guide

> Keep this file concise (≤ ~2 pages). Update it whenever recurring clarification is needed.

## 1. What This Project Does

Project Moonwalk provides automated backup and restore for ArcGIS Online (AGOL) items tagged with `Backup` in the org.

Components:

- Nightly backup job (Cloud Run) exports tagged items, packages metadata + data, versions them in Google Cloud Storage, and writes summary docs to Firestore.
- Restore service (Firebase Hosting + Functions + React UI) lists backed up items and lets an authorized user trigger a restore of a selected version.
- Authorization: Firebase blocking functions restrict sign‑in to emails present in Firestore collection `authorized-users`.

## 2. Tech Stack Overview

Frontend: React 19 + Vite 7 + TypeScript, Tailwind (with `@ugrc` preset), React Query (@tanstack), `@ugrc/utah-design-system` components.
Backend Runtime:

- Firebase Functions: Node 22 (identity blocking functions) + Python 3.11 function (`restore`).
- Scheduled Backup Job: Python 3.11 packaged as Docker image deployed to Cloud Run (invoked nightly via Cloud Scheduler) using `arcgis` API.

- Cloud Services: Firebase (Auth, Firestore, Storage, Hosting, Emulators), Google Cloud Storage (object versioning required), Cloud Run, Cloud Scheduler, AGOL REST APIs (`createReplica`, item export, publish, layer truncate/append).

Tooling: pnpm, TypeScript project references, Vitest, ESLint (@ugrc config), Prettier (multiple plugins), Ruff (Python), GitHub Actions for CI/CD, Dependabot.

## 3. Repository Structure (Key Paths)

- `/src` React web app (entry `main.tsx`, root component `App.tsx`, feature components under `src/components`).
- `/functions/node` Firebase Node identity blocking functions (`beforeCreated`, `beforeSignedIn`). Build outputs to `lib/` (tsc). Node engine 22.
- `/functions/python` Python Firebase HTTPS callable `restore` function (`main.py`). Uses `arcgis`, needs secrets.
- `/jobs` Backup job package (installable, entrypoint defined via `setup.py` / console script `backup`). Dockerfile for Cloud Run deployment.
- `/public` Static assets.
- Root configs: `firebase.json`, `tailwind.config.js`, `eslint.config.js`, tsconfigs, Vite config, lockfiles.
- CI/CD: `.github/workflows/*`, composite actions for Firebase + Cloud Run deploy.

## 4. Local Development Basics

Prerequisites: Node LTS with pnpm, Python 3.11, (optional) conda for backup job, gcloud CLI (if touching bucket versioning), Firebase CLI (installed via dev deps), Docker (for parity with Cloud Run), libkrb5 (arcgis dependency; Ubuntu CI already installs).

Frontend + Functions (watch mode):

1. `pnpm install` (root).
2. Start emulators + dev server: `pnpm run dev` (concurrently builds node functions, waits for emulator UI, runs Vite, starts Firebase emulators for functions/storage/firestore/auth).
3. (Python restore func local) Create venv: `cd functions/python && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt` (emulator detects when ready).
4. (Optional) Populate emulated Firestore/Storage by running backup job once (below) or import from `.emulator-data` if present.

Backup Job locally (to seed test data):

1. Create env: `conda create --name moonwalk-backup python=3.11` (or venv). Activate it.
2. `cd jobs && pip install -e '.[tests]'`.
3. Ensure `TAG_NAME` and `AGOL_ORG` env vars + local secrets file (`jobs/src/backup/secrets/secrets.json`) exist; then run `moonwalk-backup`.

Secrets (development):

- Backup job: `jobs/src/backup/secrets/secrets.json` (AGOL credentials, bucket name).
- Python restore function: `functions/python/secrets/secrets.json` (same keys). In production these are mounted as GCP Secret Manager secret (`SECRETS`).

Storage Bucket Versioning: Enable once in project (see README `gcloud storage buckets update ... --versioning`). Emulator bucket needs manual enablement.

## 5. Build & Test Commands

JavaScript/TypeScript:

- Lint: `pnpm run lint` (ESLint strict: no unused disable directives, zero warnings).
- Type check: `pnpm run check` (tsc -b project references: browser + vite config).
- Unit tests: `pnpm test` (Vitest, config implicit, `App.test.js`).
- Build: `pnpm run build` (runs `tsc -b` then `vite build`). Use `--mode dev` for staging deploy.

Python (jobs package):

- Install + tests: In `jobs`: `pip install -e '.[tests]' && pytest`.
- Code style: Ruff configured (line length 120); current setup via config in `pyproject.toml`.
  Python (restore function): manual requirements install; no tests yet.

## 6. CI/CD Pipelines Summary

Pull Requests:

- Python job unit tests (3.11, installs libkrb5-dev).
- UI lint, type check, tests.
- Preview Firebase deploy if PR source branch is NOT `dev` and authored by user.
  Push (dev / main):
- `dev`: deploy Firebase (staging hosting + functions) + deploy Cloud Run backup job (dev) (optionally paused based on input).
- `main`: release automation (release-composite-action) then on published release: deploy Cloud Run (prod), Firebase (prod), send notifications.
  Versioning & Releases: Conventional Commits (Angular flavor). release-composite-action manages semver + CHANGELOG.

## 7. Coding & Contribution Guidelines

Branching: Feature branches -> PR -> `dev` (integration). Release PRs (automated) merge to `main` for production.
Commits: Conventional Commits (Angular style). Scopes must match those in release action (see org action doc if adding new scopes). Keep messages imperative and succinct.
TypeScript Style: Follow ESLint config; prefer functional components + hooks; keep component files small and typed. React Query for async; avoid raw fetch (use `ky` if needed). Derive types from Firestore data model (`MoonwalkBackup`).
Python Style: Keep functions small, explicitly handle exceptions around AGOL calls. Use context managers for temp files (example: `UnzipData`). Add tests in `jobs` package for new utilities.
Error Handling: User-facing UI should catch errors (e.g., React Query `error` states). Firebase callable must raise `HttpsError` for client-friendly messages. Avoid silent broad `except Exception`; narrow if feasible (future improvement: refine broad excepts in `functions/python/main.py`).
Performance: Backup loops page through AGOL content using `advanced_search` + page size 100. Be mindful of API rate limits; batch or delay if adding heavy operations.

## 8. Notable Pending TODOs / Gaps

In `functions/python/main.py`:

- Restore: Should we restore original layer IDs?
- Group sharing not yet implemented.
- Refactor duplicated update logic between truncate/append and recreate flows.
- Determine supported updateable properties by inspecting AGOL edit payloads.
  General:
- No automated tests for restore function.
- Secrets handling could be unified.

## 9. Common Failure Points & Tips

- ArcGIS `arcgis` package requires `libkrb5-dev` + sometimes `requests-kerberos` (CI installs). If local export fails on Linux, install those libs.
- Ensure bucket versioning enabled; restore logic uses object generations. Missing versioning => restore fails (no generations).
- Emulator vs real services: The Python restore function may fail if Storage generations absent in emulator; seed data consistent with expected path structure: `short/<item_id>/backup.zip` or `long/<item_id>/backup.zip` (restore expects `category/<item_id>/upload.zip` but backup writes `backup.zip` — note mismatch: restore currently looks for `upload.zip`; backup produces `backup.zip`. If adding features touching restore inputs, align names or introduce translation layer.)
- Windows virtualenv activation differs (doc included in README). Use an actual venv for Python restore; conda envs not detected by Firebase emulator.
- Keep Node version 22 for functions (defined in package). Changing requires updating `firebase.json` if runtime config added later.
- `arcgis` currently limited to Python 3.11; do not bump to 3.13 until support lands (see README dependency updates section).

## 10. Adding a New Feature (Example Workflow)

1. Create feature branch from `dev`.
2. Implement change (e.g., display version count beside each backup): modify `BackupItem.tsx` to show `moonwalk.versions.length`.
3. Run: `pnpm run lint && pnpm run check && pnpm test` locally; ensure pass.
4. Commit using Conventional Commit: `feat(ui): show count of versions for each backup`.
5. Open PR -> verify CI green -> merge to `dev`.

## 11. Security & Access

- Authentication via UtahID federated into Firebase Auth; blocking functions enforce allow‑list from Firestore `authorized-users` collection. To authorize a user, insert doc with their email address as ID before they attempt sign-in.
- Secrets delivered via GCP Secret Manager mounting (`SECRETS`); never commit secrets.\*
- Principle of least privilege: service accounts referenced in workflows (cloud-run-sa, scheduler-sa).

## 12. When Unsure

Prefer reading existing code patterns (e.g., React Query usage in `App.tsx`, temp file handling in backup job) before introducing new libraries. Ask to update this file if recurring confusion emerges.

---

Generated Sept 2025. Keep updates targeted; avoid expanding beyond 2 pages.
