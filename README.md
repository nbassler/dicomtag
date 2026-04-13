# dicomtag
![CI](https://github.com/nbassler/dicomtag/actions/workflows/ci.yml/badge.svg)
![Dependabot](https://img.shields.io/badge/dependabot-active-brightgreen?logo=dependabot)

A simple DICOM tag editor based on PyQt6. Runs on Linux and Windows.

<img width="836" height="650" alt="image" src="https://github.com/user-attachments/assets/d62ed5c9-0315-474e-84c9-d6525791ba71" />

## Features

- Browse and edit DICOM tags in a tree view
- Supports nested sequences (SQ elements) with expandable nodes
- Inline editing of tag values — window title shows `*` when unsaved changes exist
- Save edited files via **File → Save As**
- Opens `.dcm` and `.DCM` files (via dialog or command-line argument)

## Installation

```bash
pip install .
```

Or install with dev dependencies (ruff, pytest, mypy):

```bash
pip install ".[dev]"
```

## Usage

```bash
dicomtag [file.dcm]
```

The file argument is optional — you can also open a file from **File → Open** after launch.

## Development

Run tests:

```bash
pytest
```

Run linter:

```bash
ruff check .
```

## Building

Pre-built binaries for Linux and Windows are available on the [Releases](../../releases) page.
They are built automatically when a version tag (`v*`) is pushed.
