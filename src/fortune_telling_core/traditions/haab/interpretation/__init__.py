"""Maya Haab' month interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``HAAB_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.haab import HAAB_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core haab reference interpretation data v1"

HAAB_REGISTRY = symbol_registry(_ANCHOR, "meanings", "haab.meanings", HAAB_DECK.symbols, _SOURCE)

__all__ = ["HAAB_REGISTRY"]
