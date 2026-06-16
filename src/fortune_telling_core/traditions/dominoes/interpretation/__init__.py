"""domino divination interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``DOMINOES_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.dominoes import DOMINOES_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core dominoes reference interpretation data v1"

DOMINOES_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "dominoes.meanings", DOMINOES_DECK.symbols, _SOURCE
)

__all__ = ["DOMINOES_REGISTRY"]
