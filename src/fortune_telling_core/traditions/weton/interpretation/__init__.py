"""Javanese weton (Primbon) interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``WETON_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.weton import WETON_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core weton reference interpretation data v1"

WETON_REGISTRY = symbol_registry(_ANCHOR, "meanings", "weton.meanings", WETON_DECK.symbols, _SOURCE)

__all__ = ["WETON_REGISTRY"]
