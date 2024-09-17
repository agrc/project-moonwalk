#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
setup.py
A module that installs the restore as a module
"""

from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

setup(
    name="moonwalk-restore",
    version="1.0.0",
    license="MIT",
    description="Restore process for project moonwalk",
    author="UGRC Developers",
    author_email="ugrc-developers@utah.gov",
    url="https://github.com/agrc/project-moonwalk",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    project_urls={
        "Issue Tracker": "https://github.com/agrc/project-moonwalk/issues",
    },
    keywords=["gis"],
    install_requires=["arcgis==2.*", "google-cloud-storage==2.*"],
    extras_require={
        "tests": [
            "pytest-cov==5.*",
            "pytest-instafail==0.*",
            "pytest-mock==3.*",
            "pytest-ruff==0.*",
            "pytest-watch==4.*",
            "pytest==8.*",
            "ruff==0.*",
        ]
    },
    setup_requires=[
        "pytest-runner",
    ],
    entry_points={
        "console_scripts": [
            "restore = restore.main:restore",
            "restore_local = restore.main:local_restore",
        ]
    },
)
