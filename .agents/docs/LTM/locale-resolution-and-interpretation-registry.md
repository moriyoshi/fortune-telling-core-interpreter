# Locale Resolution and Interpretation Registry

## Summary

`_locale.py` and `_interpretation_registry.py` implement this package's active locale-aware dataset selection. The resolver canonicalizes a small supported locale set, and the registry maps those locale tags to `InterpretationData` datasets.

The implementation exists in `fortune-telling-core-interpreter`, not in `fortune-telling-core`. Core remains language-neutral and supplies the structural readings consumed by this package.

## Locale Resolver

`normalize_locale(locale)` performs simple project-local normalization:

- Trims surrounding whitespace.
- Removes POSIX encoding and modifier suffixes after `.` or `@`.
- Converts underscores to hyphens.
- Rejects empty values.
- Rejects `C` and `POSIX`.
- Maps aliases before structural canonicalization.
- Accepts `language-region` tags with two-letter language and region parts.
- Canonicalizes language to lowercase and region to uppercase.

Current aliases:

| Input | Normalized |
|-------|------------|
| `zh` | `zh-CN` |
| `ko` | `ko-KR` |

Current supported locale tags:

| Locale |
|--------|
| `en-GB` |
| `en-US` |
| `fr-FR` |
| `zh-CN` |
| `zh-TW` |
| `ko-KR` |
| `pt-BR` |
| `es-ES` |
| `ja-JP` |

`resolve_locale(locale)` returns `LocaleResolution` with the original request, normalized tag, and ordered candidate tuple.

Current fallback policy:

| Normalized | Candidates |
|------------|------------|
| `en-US` | `en-US`, `en-GB` |

All other locale tags currently produce a single candidate containing the normalized tag.

## Interpretation Registry

`InterpretationRegistry` stores a mapping from locale tag to `InterpretationData`.

Lookup flow:

1. Resolve the requested locale through `resolve_locale(locale)`.
2. Iterate the ordered candidates.
3. Return the first dataset present in `datasets`.
4. If no dataset exists, return `data=None` and keep `resolved_locale` equal to the normalized locale.

`InterpretationDatasetLookup` carries:

- `data`: matched dataset or `None`.
- `requested_locale`: input string.
- `normalized_locale`: normalized resolver output.
- `resolved_locale`: candidate whose dataset matched, or the normalized locale when none matched.

The `provenance_notes` property emits stable audit strings:

- `requested_locale=<requested>`
- `resolved_locale=<resolved>`
- `locale_fallback=<normalized>-><resolved>` when the resolved locale differs from the normalized locale.

## Interaction With interpret()

The public `interpret(reading, dataset_or_registry, locale="en-GB")` helper accepts either datasets or registries.

For a registry, `interpret()` calls `registry.lookup(locale).data`. If no dataset matches, that registry contributes no entries. For a direct dataset, locale lookup is skipped. For a sequence, each item is resolved and composed in order.

This means callers can combine:

- A tarot symbol dataset.
- An astrology sign dataset.
- An astrology house dataset.
- A position or modifier dataset.
- A locale-aware registry for one dataset family.

## Dataset Families

The current dataset modules are en-GB only:

| Family | Constant | Dataset id |
|--------|----------|------------|
| Tarot Rider-Waite-Smith | `RWS_EN_GB` | `tarot.rws.en-GB.v1` |
| Astrology signs | `ASTRO_SIGN_EN_GB` | `astro.signs.en-GB.v1` |
| Astrology houses | `ASTRO_HOUSE_EN_GB` | `astro.houses.en-GB.v1` |
| Four Pillars stems | `STEM_EN_GB` | `fp.stems.en-GB.v1` |
| Four Pillars branches | `BRANCH_EN_GB` | `fp.branches.en-GB.v1` |
| Four Pillars Ten Gods | `TEN_GODS_EN_GB` | `fp.tengods.en-GB.v1` |
| Nine Star Ki stars | `STAR_EN_GB` | `nsk.stars.en-GB.v1` |
| Nine Star Ki positions | `POSITION_EN_GB` | `nsk.positions.en-GB.v1` |

`SUPPORTED_LOCALES` lists planned supported request tags, but registry behavior depends on the datasets a caller actually supplies.

## Tests

Current tests cover locale normalization, alias handling, fallback resolution, invalid locale rejection, interpretation dataset fallback lookup, registry lookup, and public `interpret()` composition.

Use this repo's venv:

```sh
./.venv/bin/ruff format src tests
./.venv/bin/ruff check src tests
./.venv/bin/mypy src tests
./.venv/bin/pytest
```

## Pitfalls

- Do not rely on `SUPPORTED_LOCALES` alone to infer dataset availability.
- Locale fallback is explicit and narrow. `en-US` falls back to `en-GB`; other locales currently do not cross-fallback.
- `normalize_locale()` rejects structurally unsupported tags before registry lookup.
- Registry provenance notes are audit metadata; they do not mutate core `Reading.provenance`.
