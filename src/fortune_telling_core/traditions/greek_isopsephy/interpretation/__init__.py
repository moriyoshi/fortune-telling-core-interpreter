"""Greek isopsephy interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``GREEK_ISOPSEPHY_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.greek_isopsephy import GREEK_ISOPSEPHY_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core greek_isopsephy reference interpretation data v1"

GREEK_ISOPSEPHY_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "greek_isopsephy.meanings", GREEK_ISOPSEPHY_DECK.symbols, _SOURCE
)

__all__ = ["GREEK_ISOPSEPHY_REGISTRY"]
