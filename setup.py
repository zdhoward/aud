from setuptools import setup, Extension
from os.path import abspath, dirname, join
from io import open

VERSION = "0.8.6"
DESCRIPTION = "aud is a python package that aims to make bulk file edits easy enough for anyone with minimal scripting or python knowledge"

here = abspath(dirname(__file__))

try:
    from m2r import parse_from_file
    long_description = parse_from_file(join(here, "README.md"))
except (FileNotFoundError, ModuleNotFoundError):
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
    keywords=["audio", "tool", "studio", "batch", "easy", "sound", "high-level"],
    install_requires=["pydub", "colorama"],
    python_requires=">=3.6.0",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Sound/Audio :: Editors",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
