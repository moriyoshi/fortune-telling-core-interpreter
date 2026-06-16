"""Vietnamese Can Chi (sexagenary stems and branches) interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``CAN_CHI_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.can_chi import CAN_CHI_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core can_chi reference interpretation data v1"

CAN_CHI_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "can_chi.meanings", CAN_CHI_DECK.symbols, _SOURCE
)

__all__ = ["CAN_CHI_REGISTRY"]
