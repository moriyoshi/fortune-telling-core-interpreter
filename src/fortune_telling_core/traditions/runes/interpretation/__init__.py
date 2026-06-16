"""Elder Futhark runes interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``RUNE_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import reversible_registry
from fortune_telling_core.traditions.runes import RUNE_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core runes reference interpretation data v1"

RUNES_REGISTRY = reversible_registry(
    _ANCHOR, "meanings", "runes.meanings", RUNE_DECK.symbols, _SOURCE
)

__all__ = ["RUNES_REGISTRY"]
