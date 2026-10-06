# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-10-06

Windows support.

### Added
- Windows launcher `Lancer-Caquot-Windows.bat` (replaces `run.bat`): checks the
Python version, installs GPU support when an NVIDIA card is present, and
recovers from an interrupted installation.
- Step-by-step Windows installation guide in the README.
- TIFF images (`.tif`, `.tiff`) and upper-case extensions (`.JPG`).
- Inventory numbers are read from file names following the "Musée de France"
convention.

### Changed
- Thesaurus files saved from Excel are accepted (`;` separator, Windows
encoding, upper-case headers).
- Downloaded models work offline.
- File and folder pickers open in front of the terminal.
- Unreadable images are listed at the end instead of stopping the batch, and
progress is saved every 20 images.
- Re-importing an image folder keeps its existing results.

### Fixed
- Thesaurus vectors were slightly different at each run (model not in
evaluation mode).
- Crashes when an action was run before a thesaurus, a model or vectors existed.
- The GPU was never used on Windows.


## [1.1.0] - 2026-10-01

### Added
- [Experimental] Added two Natural Language Processing scripts in `nlp/nlp.py.`
They allow searching through your images (text/image) or thesaurus (text/text)
using natural language.

### Changed
- The `confidence_level` field has been renamed `cosinus_similarity`, which is
more accurate.
- Several inputs have been fixed to prevent crashes caused by invalid input.
- Better and stronger way to download and delete a model. Now the data of a
model lives in `data/models`.
- Improvement of the data model for the `IMAGE` table in preparation for future
updates.
- Documentation update.
- UI redesign.


## [1.0.0] - 2026-09-10

Completion of the project's initial scope.

Complete UI redesign.
Separation of actions into dedicated modules and code refactoring.
New way to launch the project using `run.sh`/`run.bat`.

### Added
- `run.sh`/`run.bat`: new entry point for launching CAQUOT, with automatic
creation and setup of the virtual environment.
- `main.py`: a new main menu providing access to the different modules.
- `thesaurus.py`: dedicated functions for importing, listing, deleting, and
selecting thesauri.
- `model.py`: dedicated functions for importing, listing, deleting, selecting,
and loading models.
- `image.py`: dedicated function for deleting images.

### Changed
- Complete redesign of the user interface for a terminal-oriented presentation.
- Refactored the project architecture by separating actions into dedicated
modules.
- Reorganization of the project structure.
- `README.md`, `CREDITS.md`, `LICENSE.md`: documentation updates.


## [0.1.0] - 2026-09-01

Release of the project on Github.

### Added

- `db.py`: SQLite schema - tables `THESAURUS`, `IMAGE`, `CLIP_MODEL`,
`IMAGE_VECTORS`, `THESAURUS_VECTORS`, `IMAGE_THESAURUS` ; vector serialization
as BLOB.
- `embed.py`: CLIP embeddings for images and thesaurus terms.
- `alignment.py`: cross-modal similarity matching.
- `export.py`: CSV export with confidence level.
- Initial documentation (`README.md`, `PROJET.md`) and licence (`LICENSE.md`).