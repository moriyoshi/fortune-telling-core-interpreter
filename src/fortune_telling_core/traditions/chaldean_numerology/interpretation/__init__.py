"""Chaldean numerology interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``CHALDEAN_NUMEROLOGY_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.chaldean_numerology import CHALDEAN_NUMEROLOGY_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core chaldean_numerology reference interpretation data v1"

CHALDEAN_NUMEROLOGY_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "chaldean_numerology.meanings", CHALDEAN_NUMEROLOGY_DECK.symbols, _SOURCE
)

__all__ = ["CHALDEAN_NUMEROLOGY_REGISTRY"]
