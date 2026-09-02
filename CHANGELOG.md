# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2026-09-02

### Fixed

- `Distance / Duration` returned a wildly incorrect `Speed` (it divided by
  `seconds * 3600` instead of converting seconds to hours via `seconds / 3600`).

## [0.1.5] - 2026-09-01

### Fixed

- Restored `Speed` and `speed()` re-exports from the top-level `py42195`
  package (regressed in 0.1.4).

### Changed

- License metadata switched from a classifier-style table to the SPDX
  identifier `"MIT"`.

## [0.1.4] - 2024-09-23

### Changed

- Raised minimum supported Python version from 3.10 to 3.11.

### Removed

- Unused (and undeclared) `typing_extensions` runtime dependency.

## [0.1.3] - 2024-09-21

### Added

- `Speed` and `speed()` are now importable directly from the top-level
  `py42195` package (previously only from `py42195.types`).

## [0.1.2] - 2024-09-20

### Added

- Support for `timedelta / Pace`.

## [0.1.1] - 2024-09-20

### Added

- Support for `timedelta / Distance`.

## [0.1.0] - 2024-08-29

### Added

- Initial release: `Distance`, `Duration`, `Pace`, and `Speed` value types
  with metric/imperial unit systems, string parsing, and cross-type
  arithmetic (e.g. `Distance * Pace -> Duration`, `Distance / Duration ->
  Speed`).
