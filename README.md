# aud
### v0.8.6
[![CircleCI](https://circleci.com/gh/zdhoward/aud.svg?style=svg)](https://circleci.com/gh/zdhoward/aud)

- Support for Python 3.8, 3.7, & 3.6
- Support for Windows & Ubuntu
- Requires ffmpeg is already installed and updated

##### Installing FFMPEG:
```
>> On Linux:
apt-get install ffmpeg libavcodec-extra

>> On Mac:
brew install ffmpeg --with-libvorbis --with-sdl2 --with-theora

>> On Windows:
>> visit https://www.ffmpeg.org/download.html
>> download and install the appropriate package
>> ensure it is added to your PATH and you can call it from cmd
```

##### To start contributing:
```
>> git clone https://github.com/zdhoward/aud.git
>> cd aud
>> virtualenv venv
>> source venv/bin/activate
>> python3 -m pip install -r requirements.txt
>> python3 aud/. --test
```

##### Quickstart:
```
a = aud.Dir("folder", ['wav', 'mp3'], logfile="main.log")

a.log("Backing up")
a.backup("backups/todays_date/")

a.log("Changing filenames to all uppercase")
a.name_upper()

a.log("Creating exports for Amuse")
a.export_for("amuse", "exports/amuse")

a.log("add initials to all files")
a.name_append("_ZH")

a.log("Zip files up")
a.zip("my_files.zip")
```
---

# Repository Overview

This repository provides **aud**, a Python library for bulk audio file management. The project ships a `Dir` class that organizes collections of files and performs operations such as backups, renaming, audio effects, and conversions. The repository also includes a GUI prototype and a thorough test suite.

```
aud/
├── aud/ # main package (Dir class, exceptions, tests)
├── gui/ # PySimpleGUI-based prototype
├── mock_assets/ # sample audio for tests
├── API.md, README.md # documentation and quickstart
├── main.py # small example script
└── setup.py # packaging info
```

## Key Components

1. **Documentation and Quick Start**
   - The README shows how to install FFMPEG and illustrates a short workflow using the `Dir` class. Lines 23‑50 provide a setup guide and a quick usage demo.
   - `API.md` lists the major methods—core operations, configuration, renaming, audio effects, conversions, and exports. Lines 5‑38 present a concise API overview.

2. **`aud` Package**
   - `aud/aud.py` defines the `Dir` class. It tracks a working directory, manages allow/deny lists, and exposes numerous methods for manipulating files:
     - General actions (`backup`, `move`, `copy`, `zip`)
     - Configuration (`config_set_log_file`, `config_set_extensions`, etc.)
     - Naming tools (`name_upper`, `name_lower`, `name_prepend`, etc.)
     - Audio effects (`afx_normalize`, `afx_fade`, `afx_pad`, and others)
     - Conversion helpers (to WAV, MP3, FLAC, RAW, etc.)
     - Export presets via `export_for`
     - Utility functions at the bottom (e.g., `bit_depth_level`, `checkdir`, `split_filename`).
   - `aud/exceptions.py` defines custom exception classes used throughout the package.
   - `aud/__main__.py` allows running tests via `python -m aud --test`.

3. **Testing**
   - `aud/test_aud.py` exercises nearly every feature. It sets up a temporary directory with sample WAV files and verifies backup, copy, move, renaming, conversions, and exports.

4. **GUI Prototype**
   - The `gui/` directory contains early PySimpleGUI scripts (`aud-gui.py`, `gui.py`, `layouts.py`). These files lay out window components and event handling to interact with the `Dir` class. They are experiments toward a user-friendly interface but not yet production ready.

5. **Packaging**
   - `setup.py` and `setup.cfg` define package metadata. Dependencies include `pydub` (for audio processing) and `colorama` (for colored logs).

## Tips for New Contributors

- **Understand the `Dir` class**: Most functionality lives here, so browsing `aud/aud.py` gives a clear view of available operations and how they interact with the filesystem.
- **Explore the tests**: `aud/test_aud.py` demonstrates typical usage patterns and helps verify that your environment is set up correctly.
- **Look into the GUI**: If you’re interested in providing a graphical interface, the scripts in `gui/` show initial attempts with PySimpleGUI. Extending or refactoring them could be an interesting project.
- **Audio knowledge**: The code leverages FFMPEG via `pydub`. Familiarity with audio formats, sampling rates, and bit depths helps when working on conversion or FX routines.
- **Next Steps**:
  - Dive deeper into `pydub` to understand advanced audio manipulations.
  - Enhance error handling and logging for production use.
  - Consider packaging the command-line entry point or improving the GUI for non‑technical users.

Overall, **aud** is a utility-driven project aimed at simplifying large-scale audio file operations. Reviewing the Dir class methods and the accompanying tests will give you a solid grasp of how to use and extend the package.
