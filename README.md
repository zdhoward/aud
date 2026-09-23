# aud
---
[![CI](https://github.com/zdhoward/aud/actions/workflows/ci.yml/badge.svg)](https://github.com/zdhoward/aud/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

aud is a Python tool for batch audio file processing, designed for scripting, automation, and extensibility.

Version 2 is a full architectural rewrite focused on correctness, testability, and long-term maintainability rather than feature sprawl.

---

## What’s New in v2

aud v2 replaces the original monolithic implementation with a clean, modular core.

Key changes:

* Clear separation between intent (operations) and execution (adapters)
* Deterministic, test-driven behavior across all core functionality
* Explicit filesystem, audio, and conversion layers
* Modern packaging and tooling (`pyproject.toml`, pytest, coverage)
* A stable foundation for future features

Platform-specific export presets (`export_for`) are implemented as of v2.0.2, along with a broad set of correctness and validation fixes (see [CHANGELOG.md](CHANGELOG.md)).

---

## Installation

### User installation

```
pip install aud
```

### Development installation

```
pip install -e .[dev]
```

The development extra installs pytest, coverage, formatting, linting, and pre-commit tooling.

---

## Basic Usage

aud operates on directories through the `Dir` interface.

```python
from aud import Dir

d = Dir("audio")

d.config_set_extensions(["wav"])
d.name_upper()
d.convert_to_mp3()
```

Operations are applied to the current directory selection and executed through adapters.

---

## Core Concepts

### Dir

`Dir` represents a working directory and the current file selection. It is responsible for:

* scanning directories
* filtering files by extension, allowlist, and denylist
* building execution plans
* invoking the appropriate adapters

### Operations

Operations describe *what* should happen. They do not perform IO directly.

Examples include:

* renaming files
* converting audio formats
* applying audio effects
* moving or copying files

Operations are composable and independent of execution.

### Adapters

Adapters perform *how* an operation is executed.

aud currently includes adapters for:

* filesystem operations
* audio processing
* format conversion

This separation keeps behavior explicit and testable.

---

## Supported Operations

### Naming

* uppercase / lowercase
* prepend / append
* replace
* iterate
* replace spaces

Naming operations rename files on disk via the filesystem adapter.

---

### Filesystem

* copy
* move
* backup
* zip

Filesystem operations operate on the current selection and return updated file references.

---

### Audio Effects

Audio effects are applied using `pydub` and include:

* fade in / fade out
* normalization
* gain adjustment
* high-pass / low-pass filters
* silence stripping
* audio joining

---

### Format Conversion

Supported formats include:

* wav
* mp3
* ogg
* flac

Additional helpers include mono and stereo conversion.

---

## Export Presets

`export_for()` exports the current selection to a target directory using a platform preset:

```python
d = Dir("masters", extensions=["wav"])
d.export_for("cd", "cd_export")     # WAV 44.1 kHz 16-bit
d.export_for("amuse", "amuse_export")  # WAV 44.1 kHz 16-bit
d.export_for("mp3", "mp3_export")  # MP3
d.export_for("wav", "wav_export")  # WAV, source rate/depth preserved
```

Only converted copies are written to the export directory; the source files and
the current selection are left untouched. Unknown platforms raise `ExportError`.

---

## Testing

aud uses pytest for all core behavior.

```
pytest
```

Tests cover:

* directory selection logic
* configuration behavior
* naming operations
* filesystem execution
* audio effects
* format conversion
* plan previews
* adapter dispatch and error handling
* the CLI entrypoint

By default, `pytest` runs without coverage for speed. To generate a coverage report locally:

```
pytest --cov=aud --cov-report=term-missing
```

CI enforces a minimum coverage of 85%.

---

## Project Structure

```
aud/
├── aud.py               # Dir interface
├── cli.py               # CLI entrypoint
├── core/
│   ├── adapters/        # Execution layers
│   ├── operations/     # Intent definitions
│   ├── selection/      # File selection logic
│   ├── models.py
│   └── plan.py
├── exceptions.py
└── __main__.py
```

---

## Status

aud v2 is stable and fully tested (74 tests, 92% coverage, 85% CI gate).

The core architecture is complete. Planned work is tracked in
[ROADMAP.md](ROADMAP.md) and in the GitHub issue tracker: data-safety
guards and performance work target v2.1.0, a real CLI targets v2.2.0,
and an optional web UI is planned as a separate install.

## Documentation

* [API.md](API.md) — API reference
* [EXAMPLES.md](EXAMPLES.md) — recipes and workflows
* [CHANGELOG.md](CHANGELOG.md) — release history
* [ROADMAP.md](ROADMAP.md) — maintenance priorities and planned versions
* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — design overview and extension points

---

## License

MIT License
