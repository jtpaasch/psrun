"""The ``setup.py`` file for the package."""

from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="psrun",
    version="1.0.0",
    description="Runs commands and monitors them",
    long_description=long_description,
    packages=find_packages(
        exclude=["venv", "tests"]
    ),
    install_requires=["psutil", "flake8", "coverage"],
    entry_points={
        "console_scripts": [
            "psrun = psrun.cli.main:cli"
        ],
    },
)
