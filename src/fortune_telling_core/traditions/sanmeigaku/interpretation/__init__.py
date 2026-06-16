"""Sanmeigaku (算命学) star interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols (ten main stars and twelve subordinate stars) come from core's
``SANMEIGAKU_DECK``. See :mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.sanmeigaku import SANMEIGAKU_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core sanmeigaku reference interpretation data v1"

SANMEIGAKU_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "sanmeigaku.meanings", SANMEIGAKU_DECK.symbols, _SOURCE
)

__all__ = ["SANMEIGAKU_REGISTRY"]
