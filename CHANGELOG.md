# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.1.0] - 2026-09-01

Release of the project on Github.

### Added

- db.py : SQLite schema - tables THESAURUS, IMAGE, CLIP_MODEL, IMAGE_VECTORS,
THESAURUS_VECTORS, IMAGE_THESAURUS ; vector serialization as BLOB.
- embed.py : CLIP embeddings for images and thesaurus terms.
- alignment.py : cross-modal similarity matching.
- export.py : CSV export with confidence level.
- Initial documentation (README.md, PROJET.md) and licence (LICENSE.md).