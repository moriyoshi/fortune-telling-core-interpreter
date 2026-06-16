"""Petit Lenormand interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``LENORMAND_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.lenormand import LENORMAND_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core lenormand reference interpretation data v1"

LENORMAND_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "lenormand.meanings", LENORMAND_DECK.symbols, _SOURCE
)

__all__ = ["LENORMAND_REGISTRY"]
