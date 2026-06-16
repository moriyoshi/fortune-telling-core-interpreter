# fortune-telling-core-interpreter Overview

`fortune-telling-core-interpreter` is the interpretation and locale layer for `fortune-telling-core` readings. It contributes interpretation contracts, a public `interpret()` helper, locale-aware dataset lookup, and English reference datasets to the `fortune_telling_core` namespace.

The package is designed to be installed alongside the sibling `../fortune-telling-core` checkout. Core owns structural readings, tradition engines, symbols, provenance, errors, coercion helpers, and serialization types. Interpreter consumes those stable structural objects and adds discretionary meaning text outside the core engine layer.

## Scope

This package provides:

* `fortune_telling_core.interpretation`: interpretation keys, entries, mapping-backed datasets, and `interpret()`.
* `fortune_telling_core._interpretation_registry`: locale-aware dataset registry lookup.
* `fortune_telling_core._locale`: locale normalization, aliases, and fallback candidates.
* `fortune_telling_core.traditions.*.interpretation`: per-tradition English reference datasets.

This package does not provide:

* Structural reading engines.
* Tarot draw mechanics, astrology calculations, Four Pillars chart calculation, or Nine Star Ki chart calculation.
* Core serialization primitives, validation errors, or provenance models.

## Current Traditions

The current reference datasets cover:

* Tarot Rider-Waite-Smith meanings in `tarot.rws.en-GB.v1`.
* Astrology sign and house placement meanings in `astro.signs.en-GB.v1` and `astro.houses.en-GB.v1`.
* Four Pillars stems, branches, and Ten Gods in `fp.stems.en-GB.v1`, `fp.branches.en-GB.v1`, and `fp.tengods.en-GB.v1`.
* Nine Star Ki stars and positions in `nsk.stars.en-GB.v1` and `nsk.positions.en-GB.v1`.

## Agent Notes

Use this repo's own `./.venv` for all Python commands. Install the sibling core checkout into that venv with `./.venv/bin/pip install -e ../fortune-telling-core -e . ruff mypy pytest`.
