"""I Ching (Book of Changes) interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``ICHING_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.iching import ICHING_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core iching reference interpretation data v1"

ICHING_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "iching.meanings", ICHING_DECK.symbols, _SOURCE
)

__all__ = ["ICHING_REGISTRY"]
