"""Japanese koyomi (六曜 rokuyō) interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``KOYOMI_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.koyomi import KOYOMI_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core koyomi reference interpretation data v1"

KOYOMI_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "koyomi.meanings", KOYOMI_DECK.symbols, _SOURCE
)

__all__ = ["KOYOMI_REGISTRY"]
