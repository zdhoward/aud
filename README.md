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

Some ideas present in earlier versions (such as platform-specific export presets) were never fully implemented and are intentionally deferred in v2.

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

`export_for()` exists as a placeholder for future platform-specific export presets.

This behavior was never fully implemented in earlier versions and is intentionally deferred in v2. The method is retained as a clear extension point for future development.

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

Coverage is intentionally focused on core logic rather than CLI entrypoints.

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

aud v2 is stable and fully tested.

The core architecture is complete. Future development will focus on adding new operations and higher-level workflows built on the existing foundation.

---

## License

MIT License
