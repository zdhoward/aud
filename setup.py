from setuptools import setup, Extension
from os.path import abspath, dirname, join
from io import open
from m2r import parse_from_file

VERSION = "0.8.1"
DESCRIPTION = "aud is a python package that aims to make bulk file edits easy enough for anyone with minimal scripting or python knowledge"

here = abspath(dirname(__file__))

try:
    long_description = parse_from_file(join(here, "README.md"))
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name="aud",
    packages=["aud"],
    version=VERSION,
    license="MIT",
    description=DESCRIPTION,
    author="Zach Howard",
    author_email="zach.d.howard@gmail.com",
    url="https://github.com/zdhoward/aud",
    keywords=["audio", "studio", "batch", "easy"],
    install_requires=["pydub", "colorama"],
    python_requires=">=3.6.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
