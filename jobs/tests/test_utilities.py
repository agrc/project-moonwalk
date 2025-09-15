#!/usr/bin/env python
# * coding: utf8 *
"""Unit tests for utilities module.

All external service calls (GCS, Firestore, ArcGIS) are mocked.
"""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

# Ensure module does not initialize real clients
os.environ.setdefault("CI", "1")

from backup import utilities  # noqa: E402  (import after setting CI)


def test_add_to_zip():
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "test.zip"
        utilities.add_to_zip(zip_path, [("test_file.txt", "This is a test file.")])
        with ZipFile(zip_path, "r") as zip_file:
            assert "test_file.txt" in zip_file.namelist()
            with zip_file.open("test_file.txt") as file_in_zip:
                assert file_in_zip.read().decode("utf-8") == "This is a test file."


def test_get_secrets_local(monkeypatch, tmp_path):
    # Craft a fake local secrets folder by pointing __file__ to temp dir
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "secrets.json").write_text('{"BUCKET_NAME": "test-bucket"}', encoding="utf-8")

    original_file = utilities.__file__
    try:
        utilities.__file__ = str(tmp_path / "dummy.py")  # so parent/secrets resolves to our temp dir
        secrets = utilities.get_secrets()
        assert secrets["BUCKET_NAME"] == "test-bucket"
    finally:
        utilities.__file__ = original_file


def test_get_secrets_not_found(monkeypatch, tmp_path):
    # Point __file__ somewhere with no secrets folder
    original_file = utilities.__file__
    try:
        utilities.__file__ = str(tmp_path / "dummy.py")
        with pytest.raises(FileNotFoundError):
            utilities.get_secrets()
    finally:
        utilities.__file__ = original_file


def test_ensure_export_ready_adds_extract(monkeypatch):
    updated_payload = {}

    class DummyManager:
        def __init__(self):
            self.properties = SimpleNamespace(capabilities="Query,Update")

        def update_definition(self, payload):
            updated_payload["payload"] = payload

    class DummyFLC:
        @classmethod
        def fromitem(cls, fs_item):  # noqa: D401
            return SimpleNamespace(manager=DummyManager())

    monkeypatch.setattr(utilities, "FeatureLayerCollection", DummyFLC)

    utilities.ensure_export_ready({})

    assert "Extract" in updated_payload["payload"]["capabilities"]


def test_ensure_export_ready_no_action(monkeypatch):
    class DummyManager:
        def __init__(self):
            self.properties = SimpleNamespace(capabilities="Query,Update,Extract")
            self.called = False

        def update_definition(self, payload):  # pragma: no cover - should not be called
            self.called = True

    dummy_manager = DummyManager()

    class DummyFLC:
        @classmethod
        def fromitem(cls, fs_item):
            return SimpleNamespace(manager=dummy_manager)

    monkeypatch.setattr(utilities, "FeatureLayerCollection", DummyFLC)

    utilities.ensure_export_ready({})

    assert dummy_manager.properties.capabilities.count("Extract") == 1
    assert dummy_manager.called is False
