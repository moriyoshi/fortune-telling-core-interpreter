# fortune-telling-core-interpreter

`fortune-telling-core-interpreter` contributes interpretation contracts,
locale-aware registries, and reference datasets — covering every core tradition
across 18 locales — to the `fortune_telling_core` namespace. The sibling
[`fortune-telling-core`](https://pypi.org/project/fortune-telling-core/) library
supplies structural readings, engines, decks, spreads, and symbols; this package
maps those stable structural ids to discretionary interpretation text.

## What it adds

This is a namespace-package extension. It ships no top-level package of its own;
it adds modules under the existing `fortune_telling_core` namespace:

- `fortune_telling_core.interpretation` - data contracts (`InterpretationKey`,
  `InterpretationEntry`, `MappingInterpretationData`), the `interpret()` resolver
  that turns a core `Reading` into per-position text, and `interpret_extras()`
  for off-grid selections (e.g. astrology aspects in `draw.extras`). Exposes the
  distribution `__version__`.
- `fortune_telling_core._interpretation_registry` - `InterpretationRegistry`, a
  locale-indexed lookup over a dataset family.
- `fortune_telling_core._locale` - locale normalization and fallback policy.
- `fortune_telling_core.traditions.*.interpretation` - reference datasets for
  every core tradition (tarot, astrology, Four Pillars, Nine Star Ki, I Ching,
  Lenormand, runes, dominoes, geomancy, Tzolk'in, Can Chi, Celtic tree, Thaksa,
  weton, the numerology/gematria systems, CJK name strokes, Haab', koyomi,
  Sanmeigaku, Sukuyō, and Zi Wei Dou Shu), each with a prebuilt locale registry.
  The four original families use template + vocabulary bundles; most newer ones
  use per-symbol meaning bundles; a few are keyed by spread position (Zi Wei
  palaces) or by a computed value (CJK stroke-count luck, astrology aspects).

Time-varying readings are supported through core's `ReadingRequest.as_of`:
astrology gains interpreted transit-to-natal aspects, and the East-Asian systems
gain their annual/luck-cycle periods. All non-English text is machine-translated
reference data pending native-speaker review.

## Getting started

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

See the **API Reference** for the generated documentation of every public symbol.
