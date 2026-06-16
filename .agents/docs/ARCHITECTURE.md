# Architecture

## Namespace Package Boundary

`fortune-telling-core-interpreter` extends the `fortune_telling_core` namespace supplied by the sibling `../fortune-telling-core` package. Core ships the `pkgutil.extend_path` declarations in its `__init__.py` files. This package intentionally has no top-level `src/fortune_telling_core/__init__.py`.

The interpreter package contributes root modules and leaf interpretation packages:

* `src/fortune_telling_core/interpretation.py`
* `src/fortune_telling_core/_interpretation_registry.py`
* `src/fortune_telling_core/_locale.py`
* `src/fortune_telling_core/traditions/*/interpretation/`

The leaf `*/interpretation/__init__.py` files export dataset constants for their traditions. Parent tradition packages remain owned by core.

## Interpretation Contract

`interpretation.py` defines the data contract for meaning lookup:

* `InterpretationKey`: stable lookup key with `symbol_id`, optional `position_id`, and optional `variant`.
* `InterpretationEntry`: text, keywords, source, and the key it answers.
* `InterpretationData`: protocol for datasets that expose a stable `id` and `lookup(key)`.
* `MappingInterpretationData`: immutable mapping-backed dataset with duplicate-key validation and fallback lookup.
* `interpret()`: public helper that resolves entries for each position in a structural core `Reading`.

`interpret()` accepts a single dataset, a locale-aware registry, or a sequence of datasets and registries. It walks `reading.positions`, derives candidate keys from each `PositionReading`, and returns a dictionary keyed by spread position id.

Candidate key generation is structural:

* The primary key uses `position.symbol.id`, `selection.position_id`, and a variant derived from modifiers.
* Tarot orientation uses the `orientation` modifier.
* Astrology retrograde handling maps `retrograde=true` to the `retrograde` variant.
* Four Pillars stem readings use non-day-master `ten_god` modifiers as variants.
* Element modifiers are used as a final variant fallback.
* Astrology house modifiers add `astro.house.<number>` candidates.
* Nine Star Ki position text uses the synthetic `nsk.position` symbol id with the reading position id.

When multiple datasets resolve entries for the same position, `_merge_entries()` concatenates text, deduplicates keywords, and joins unique sources. This supports combining symbol, house, position, and tradition-specific datasets.

## Registry and Locale Lookup

`_interpretation_registry.py` provides:

* `InterpretationRegistry`: a locale-indexed collection of `InterpretationData` objects for one dataset family.
* `InterpretationDatasetLookup`: lookup result containing the requested, normalized, and resolved locale plus the matched dataset if any.

The registry calls `resolve_locale(locale)` and tries each candidate locale in order. If no dataset matches, it returns `data=None` with `resolved_locale` set to the normalized locale.

`InterpretationDatasetLookup.provenance_notes` returns audit strings such as `requested_locale=en_US`, `resolved_locale=en-GB`, and `locale_fallback=en-US->en-GB` when fallback occurs.

## Locale Resolution

`_locale.py` implements a small project-owned locale policy rather than full BCP 47 negotiation.

`SUPPORTED_LOCALES` currently contains:

* `en-GB`
* `en-US`
* `fr-FR`
* `zh-CN`
* `zh-TW`
* `ko-KR`
* `pt-BR`
* `es-ES`
* `ja-JP`

Aliases currently map:

* `zh` to `zh-CN`
* `ko` to `ko-KR`

Fallbacks currently map:

* `en-US` to `en-GB`

`normalize_locale()` strips POSIX suffixes such as `.UTF-8` and `@modifier`, accepts underscore input such as `en_US`, canonicalizes language and region case, and rejects empty, `C`, `POSIX`, and structurally unsupported tags.

## Datasets

The current implementation ships English en-GB datasets:

* `tarot/interpretation/rws_en.py`: `RWS_EN_GB`, dataset id `tarot.rws.en-GB.v1`.
* `astrology/interpretation/signs_en.py`: `ASTRO_SIGN_EN_GB`, dataset id `astro.signs.en-GB.v1`.
* `astrology/interpretation/houses_en.py`: `ASTRO_HOUSE_EN_GB`, dataset id `astro.houses.en-GB.v1`.
* `four_pillars/interpretation/stems_en.py`: `STEM_EN_GB`, dataset id `fp.stems.en-GB.v1`.
* `four_pillars/interpretation/branches_en.py`: `BRANCH_EN_GB`, dataset id `fp.branches.en-GB.v1`.
* `four_pillars/interpretation/ten_gods_en.py`: `TEN_GODS_EN_GB`, dataset id `fp.tengods.en-GB.v1`.
* `nine_star_ki/interpretation/stars_en.py`: `STAR_EN_GB`, dataset id `nsk.stars.en-GB.v1`.
* `nine_star_ki/interpretation/positions_en.py`: `POSITION_EN_GB`, dataset id `nsk.positions.en-GB.v1`.

Dataset modules import structural constants from core, then build `MappingInterpretationData` entries against core symbol ids, position ids, modifiers, and attributes.

## Dependency Direction

Interpreter depends on core. Core must not depend on interpreter.

Interpreter imports private core helpers `fortune_telling_core.coerce` and `fortune_telling_core.serde_types` for validation and JSON-compatible typing. That is an intentional package split compromise: the helper implementations remain in core, while interpretation data moved into this package.

## Tests

Tests live under `tests/` and exercise:

* Locale normalization and fallbacks.
* Interpretation entry serialization and lookup fallbacks.
* Public `interpret()` composition over core readings.
* Tradition-specific dataset lookup for astrology and tarot.

Run the local gate with this repo's venv:

```sh
./.venv/bin/ruff format src tests
./.venv/bin/ruff check src tests
./.venv/bin/mypy src tests
./.venv/bin/pytest
```
