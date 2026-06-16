"""CJK name-stroke (five-grid) onomancy interpretation datasets across locales.

Two composing registries:

- :data:`CJK_NAME_STROKES_REGISTRY` - the per-grid axis meaning (what each of the
  five grids signifies), one entry per deck symbol from ``locales/meanings/``.
- :data:`CJK_NAME_STROKES_STROKE_COUNT_REGISTRY` - the luck reading for each
  grid's resolved stroke count (1-81), from ``locales/stroke_count/``. This is
  the default rating scheme; :data:`STROKE_COUNT_REGISTRIES` holds one
  registry per selectable scheme (e.g. ``"kumazaki"``, ``"chinese_wuge"``).

``interpret`` merges them, so a grid's text is its axis sentence followed by the
reading for its actual stroke count. The symbols come from core's
``CJK_NAME_STROKES_DECK``. See :mod:`fortune_telling_core._symbol_interpretation`
and :mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.cjk_name_strokes import CJK_NAME_STROKES_DECK
from fortune_telling_core.traditions.cjk_name_strokes.interpretation.stroke_count import (
    CJK_NAME_STROKES_STROKE_COUNT_EN_GB,
    CJK_NAME_STROKES_STROKE_COUNT_EN_US,
    CJK_NAME_STROKES_STROKE_COUNT_JA_JP,
    CJK_NAME_STROKES_STROKE_COUNT_REGISTRY,
    DEFAULT_SCHEME,
    SCHEMES,
    STROKE_COUNT_RATINGS,
    STROKE_COUNT_REGISTRIES,
)

_ANCHOR = __name__
_SOURCE = "fortune-telling-core cjk_name_strokes reference interpretation data v1"

CJK_NAME_STROKES_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "cjk_name_strokes.meanings", CJK_NAME_STROKES_DECK.symbols, _SOURCE
)

__all__ = [
    "CJK_NAME_STROKES_REGISTRY",
    "CJK_NAME_STROKES_STROKE_COUNT_EN_GB",
    "CJK_NAME_STROKES_STROKE_COUNT_EN_US",
    "CJK_NAME_STROKES_STROKE_COUNT_JA_JP",
    "CJK_NAME_STROKES_STROKE_COUNT_REGISTRY",
    "DEFAULT_SCHEME",
    "SCHEMES",
    "STROKE_COUNT_RATINGS",
    "STROKE_COUNT_REGISTRIES",
]
