# dicomtag

A simple DICOM tag editor based on PyQt6. Runs on Linux and Windows.

![image](https://github.com/user-attachments/assets/f9b9d009-1dfe-4af2-9169-33dbc011169c)

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
