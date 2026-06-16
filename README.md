# fortune-telling-core-interpreter

`fortune-telling-core-interpreter` contributes interpretation contracts,
locale-aware registries, and reference interpretation datasets to the
`fortune_telling_core` namespace.

It is a namespace-package extension for
[`fortune-telling-core`](https://pypi.org/project/fortune-telling-core/): the
core package supplies readings, engines, decks, spreads, and symbols, while this
package supplies the discretionary interpretation layer:

- `fortune_telling_core.interpretation` - data contracts, the `interpret()`
  resolver (per spread position), and `interpret_extras()` for off-grid
  selections such as astrology aspects.
- `fortune_telling_core._interpretation_registry` - `InterpretationRegistry` for
  locale-aware dataset selection.
- `fortune_telling_core._locale` - locale normalization and fallback policy.
- `fortune_telling_core.traditions.*.interpretation` - reference datasets for
  every core tradition. The original four (tarot, astrology, Four Pillars, Nine
  Star Ki) use template + vocabulary bundles; most newer traditions (I Ching,
  Lenormand, runes, dominoes, geomancy, Tzolk'in, Can Chi, Celtic tree, Thaksa,
  weton, Haab', koyomi, Sanmeigaku, Sukuyō, and the numerology/gematria systems)
  use per-symbol meaning bundles via `fortune_telling_core._symbol_interpretation`;
  Zi Wei Dou Shu is keyed by the twelve palaces (the spread position) rather than
  by deck symbol. Each tradition exposes a
  prebuilt `*_REGISTRY`.

## Install

```bash
python -m pip install fortune-telling-core-interpreter
```

The required `fortune-telling-core` dependency is installed automatically.

## Quick start

Resolve interpretation entries for a structural core reading. `interpret()`
returns a mapping from spread position id to a resolved `InterpretationEntry`:

```python
from fortune_telling_core import RandomRng, ReadingRequest
from fortune_telling_core.interpretation import interpret
from fortune_telling_core.traditions.tarot import RWS_DECK, SINGLE_CARD, build_engine
from fortune_telling_core.traditions.tarot.interpretation import RWS_EN_GB

engine = build_engine()
reading = engine.read(
    ReadingRequest(deck_id=RWS_DECK.id, spread_id=SINGLE_CARD.id),
    rng=RandomRng(seed=42),
)

entries = interpret(reading, RWS_EN_GB, locale="en-GB")
for position_id, entry in entries.items():
    print(position_id, entry.text)
```

Use an `InterpretationRegistry` to select a dataset by locale, with normalization
and fallback (for example `en-US` falls back to `en-GB` when no en-US dataset is
registered):

```python
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.traditions.tarot.interpretation import RWS_EN_GB

registry = InterpretationRegistry(datasets={"en-GB": RWS_EN_GB})
entries = interpret(reading, registry, locale="en_US")
```

## Locales

Every dataset family — astrology signs and houses, Four Pillars stems, branches,
and Ten Gods, Nine Star Ki stars and positions, and the full 78-card
Rider-Waite-Smith tarot deck — ships in 18 locales: **en-GB**, **en-US**,
**fr-FR**, **de-DE**, **ja-JP**, **zh-CN**, **zh-TW**, **pt-BR**, **es-ES**,
**ru-RU**, **id-ID**, **vi-VN**, **th-TH**, **hi-IN**, **bn-IN**, **te-IN**,
**mr-IN**, and **ta-IN**. (Locales beyond the original four are
machine-translated reference data and benefit from native-speaker review.) Each
family exports a prebuilt registry, so a caller can resolve interpretation by
locale without assembling one:

```python
from fortune_telling_core.interpretation import interpret
from fortune_telling_core.traditions.astrology.interpretation import (
    ASTRO_HOUSE_REGISTRY,
    ASTRO_SIGN_REGISTRY,
)

entries = interpret(reading, (ASTRO_SIGN_REGISTRY, ASTRO_HOUSE_REGISTRY), locale="ja-JP")
```

Locale tags are normalized (`ja_jp` -> `ja-JP`). A bare ISO 639 language code is
accepted too and maps to its default supported locale (`fr` -> `fr-FR`,
`ja` -> `ja-JP`; `en` -> `en-GB` and `zh` -> `zh-CN` where a language has more than
one territory). The resolver also falls back per its policy (for example
`en-US` -> `en-GB` when no en-US dataset is registered).

### Translation data

Interpretation **text is data, not code**. Each dataset family ships one JSON
bundle per locale under `<family>/interpretation/locales/<dataset>/<locale>.json`:

```json
{
  "schema_version": 1,
  "locale": "fr-FR",
  "templates": { "placement": "En {sign}, {body} s'exprime ..." },
  "vocab": { "signs": { "aries": "Bélier" }, "bodies": { "sun": "le Soleil" } }
}
```

The dataset builders stay in code and keep deriving structure (lookup keys,
keyword tokens, the set and order of signs/stems/cards) from `fortune-telling-core`;
a bundle only supplies the translatable `templates` and `vocab` strings. en-GB,
fr-FR, and ja-JP are authored bundles; **en-US is derived** from en-GB in code by
British -> American spelling normalization, so it never drifts. Adding a locale is
normally a matter of adding bundle files. See
`fortune_telling_core._interpretation_bundle` for the schema and loader.

## Demo CLI

The package installs a `fortune-telling-interpret` console script that builds a
reading with a core engine and resolves localized interpretation text for it -
a companion to core's `fortune-telling-demo`:

```bash
fortune-telling-interpret --list-traditions          # each tradition's required inputs
fortune-telling-interpret tarot --seed 42            # one drawn tradition
fortune-telling-interpret greek-isopsephy --name Σωκράτης --locale fr-FR
fortune-telling-interpret --seed 7                    # all drawn traditions; rest reported
fortune-telling-interpret --list-locales             # show available locales
fortune-telling-interpret tarot --seed 42 --json     # reading + interpretation as JSON
fortune-telling-interpret astrology --birth-datetime 1990-05-15T08:30+09:00 \
  --latitude 35 --longitude 139 --as-of 2026-03-01T12:00+00:00   # natal + transits
```

It covers all 26 traditions. **Engine inputs have no defaults** — each tradition
requires its own parameters, and the CLI never calls an engine without them (it
reports what is missing instead). Run `--list-traditions` to see them; they fall
into four groups:

| Group | Traditions | Inputs |
| --- | --- | --- |
| Drawn deck | tarot, runes, lenormand, iching, dominoes, geomancy | `--seed` |
| Birth chart | astrology, four-pillars, nine-star-ki | `--birth-datetime`, `--latitude`, `--longitude` (four-pillars also `--gender`) |
| Birth date | can-chi, celtic-tree, numerology, thaksa, tzolkin, weton, haab, koyomi, sanmeigaku, sukuyo, zi-wei | `--birth-datetime` |

`--as-of <now|ISO datetime>` is the unified reference time for **timed fortunes**: it
adds transit-to-natal aspects (astrology), the 流年 annual period and 大運/大限 luck
cycles (four-pillars, nine-star-ki, sanmeigaku, zi-wei), and selects the almanac
date (koyomi). It is optional — without it the natal/birth reading stays timeless.
`--target-year` overrides `--as-of` for four-pillars and nine-star-ki.

Astrology renders its aspects too, not just sign/house placements: a natal
**Aspects** block always, and a **Transits** block (transit-to-natal) when
`--as-of` is set. These come from core's structured `Draw.extras` and are
interpreted per aspect type (conjunction/opposition/trine/square/sextile).
| Name | chaldean-numerology, name-numerology, cyrillic-pythagorean, cyrillic-slavonic-numerals, greek-isopsephy | `--name` (in the tradition's script) |
| Name (CJK) | cjk-name-strokes | `--surname`, `--given-name` |

Running a named tradition without its inputs is a usage error (exit 2) and the
engine is not called. In `all` mode, traditions whose inputs are supplied build
and the rest are reported as skipped (exit 0); a script-specific `--name` is
applied only to the name traditions whose script it matches. `--locale` (default
`en-GB`) and `--positions` are presentation options. Output is deterministic for
given inputs.

## Layout

```text
.
├── AGENTS.md
├── LICENSE
├── README.md
├── pyproject.toml
├── mkdocs.yml
├── src/
│   └── fortune_telling_core/      # namespace contributions only (no top-level __init__)
├── docs/
├── tests/
└── .agents/
    └── docs/
```

## Development

This package extends the `fortune_telling_core` namespace owned by the sibling
core project, so it is normally developed against a local
`../fortune-telling-core` checkout. Use a per-repo virtualenv at `./.venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ../fortune-telling-core -e ".[dev]"
```

Run the gate:

```bash
ruff format --check .
ruff check .
mypy src tests
pytest
```

## Documentation

The API docs are generated by mkdocstrings, which reads this package's half of
the `fortune_telling_core` namespace statically from `src`. Build the docs in an
environment where `fortune-telling-core` is **not** installed: a real core
package owns `fortune_telling_core/__init__.py` and would shadow these namespace
contributions on `sys.path`, hiding them from the doc generator.

```bash
python3 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install "mkdocs>=1.6.1" "mkdocs-material>=9.7" "mkdocstrings[python]>=1.0"
python -m pip install --no-deps -e .
mkdocs serve          # or: mkdocs build --strict
```

## Releasing

The version is **derived from the git tag** by hatch-vcs (no hand-edited literal):
tag the release `vX.Y.Z` and the build stamps that version into the wheel and a
generated `fortune_telling_core/_interpreter_version.py` (git-ignored), exposed as
`fortune_telling_core.interpretation.__version__`. The package depends on
`fortune-telling-core>=1.1.0` (for `Draw.extras` and `ReadingRequest.as_of`).

Distributions are built with hatchling and published to PyPI by the `CD`
workflow on a published GitHub Release, using PyPI Trusted Publishing (OIDC).
To build locally:

```bash
python -m pip install -e ".[release]"
git tag v1.0.0          # hatch-vcs reads this; an untagged tree builds a 0.x.devN version
python -m build
python -m twine check dist/*
```

## Licence

`fortune-telling-core-interpreter` is MIT licensed; see [LICENSE](./LICENSE).
