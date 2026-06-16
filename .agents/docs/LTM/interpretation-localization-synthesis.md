# Interpretation Localization Synthesis

## Summary

`fortune-telling-core-interpreter` is the live locale-aware interpretation layer for structural readings produced by `fortune-telling-core`. It keeps discretionary meaning text and localization outside core while using core's stable reading, symbol, position, modifier, validation, and serialization primitives.

The package extends the `fortune_telling_core` namespace and contributes interpretation modules plus per-tradition English datasets. It must be installed alongside `fortune-telling-core`.

## Stable Knowledge

- Core owns structural readings and engines; interpreter owns interpretation contracts, dataset lookup, locale resolution, and bundled meaning text.
- The sibling core package supplies `pkgutil.extend_path` in its `__init__.py` files. This repo ships no top-level `src/fortune_telling_core/__init__.py`.
- Interpreter contributes root modules under `fortune_telling_core` and leaf `fortune_telling_core.traditions.*.interpretation` packages.
- `InterpretationData` is the dataset protocol. Datasets expose a stable `id` and `lookup(InterpretationKey)`.
- `interpret()` accepts one dataset, one registry, or a sequence of datasets and registries, then returns entries keyed by core spread position id.
- Locale-aware lookup is optional at the `interpret()` boundary. Passing a registry uses the requested locale; passing a dataset bypasses registry lookup.
- Current bundled datasets are en-GB reference datasets. `en-US` locale requests can fall back to en-GB through the registry when only en-GB data exists.

## Implementation Shape

`src/fortune_telling_core/interpretation.py` defines:

- `InterpretationKey`: `symbol_id`, optional `position_id`, and optional `variant`.
- `InterpretationEntry`: text, keywords, source, and key.
- `InterpretationData`: dataset protocol.
- `MappingInterpretationData`: immutable mapping-backed implementation with duplicate-key validation.
- `interpret()`: public helper for resolving interpretation entries over a core `Reading`.

`MappingInterpretationData.lookup()` tries:

1. Exact `symbol_id`, `position_id`, and `variant`.
2. `symbol_id` plus `variant`.
3. `symbol_id` plus `position_id`.
4. `symbol_id` only.

`interpret()` creates candidate keys from each `PositionReading`. It uses the selected symbol id, spread position id, and variant derived from structural modifiers. It can also add astrology house and Nine Star Ki position candidates. When multiple datasets return entries, it merges text, keywords, and sources.

## Locale and Registry Flow

`src/fortune_telling_core/_locale.py` normalizes simple locale tags and returns lookup candidates. It intentionally implements the project's current locale policy rather than full BCP 47 negotiation.

`src/fortune_telling_core/_interpretation_registry.py` defines `InterpretationRegistry`, which maps locale tags to datasets. `lookup(locale)` resolves the requested locale, checks candidate tags in order, and returns an `InterpretationDatasetLookup`.

The lookup result records:

- `data`: matched dataset or `None`.
- `requested_locale`: original input.
- `normalized_locale`: canonical tag after normalization.
- `resolved_locale`: locale whose dataset matched, or the normalized locale when none matched.

`provenance_notes` exposes audit strings for requested locale, resolved locale, and fallback when fallback occurred.

## Bundled Datasets

The package currently ships:

- Tarot: `RWS_EN_GB` in `tarot/interpretation/rws_en.py`, dataset id `tarot.rws.en-GB.v1`.
- Astrology: `ASTRO_SIGN_EN_GB` and `ASTRO_HOUSE_EN_GB`, dataset ids `astro.signs.en-GB.v1` and `astro.houses.en-GB.v1`.
- Four Pillars: `STEM_EN_GB`, `BRANCH_EN_GB`, and `TEN_GODS_EN_GB`, dataset ids `fp.stems.en-GB.v1`, `fp.branches.en-GB.v1`, and `fp.tengods.en-GB.v1`.
- Nine Star Ki: `STAR_EN_GB` and `POSITION_EN_GB`, dataset ids `nsk.stars.en-GB.v1` and `nsk.positions.en-GB.v1`.

The dataset modules import structural constants from core and generate `InterpretationEntry` values against core ids. This keeps text data coupled to stable structural ids, not to rendered summaries.

## Operational Guidance

- Keep structural mechanics in `fortune-telling-core`; add meaning text and locale-specific data here.
- Do not add `src/fortune_telling_core/__init__.py` to this repo.
- Use this repo's `./.venv` and install the sibling core checkout into it before running checks.
- When adding a locale, update `_locale.py`, add dataset modules or registry mappings, and add tests for normalization, fallback, and lookup behavior.
- When adding a tradition dataset, use `MappingInterpretationData`, stable core ids, and focused lookup tests.

## Files

- `src/fortune_telling_core/interpretation.py`: interpretation contracts, mapping dataset, and public `interpret()`.
- `src/fortune_telling_core/_locale.py`: locale normalization, aliases, supported locale set, and fallback candidates.
- `src/fortune_telling_core/_interpretation_registry.py`: registry lookup and provenance notes.
- `src/fortune_telling_core/traditions/*/interpretation/`: bundled tradition datasets.
- `tests/core/test_interpretation.py`: core interpretation contract and public helper coverage.
- `tests/core/test_locale.py`: locale resolver coverage.

## Pitfalls

- Parent namespace packages come from core. Adding parent `__init__.py` files here can break namespace composition.
- `SUPPORTED_LOCALES` is a policy declaration, not proof that all listed locale datasets exist.
- Registry fallback can only return datasets actually present in `InterpretationRegistry.datasets`.
- Dataset ids should be stable and versioned because downstream products may record them.
