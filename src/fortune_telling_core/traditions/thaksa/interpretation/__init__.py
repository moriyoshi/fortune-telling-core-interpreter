"""Thai Thaksa (planetary) astrology interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``THAKSA_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.thaksa import THAKSA_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core thaksa reference interpretation data v1"

THAKSA_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "thaksa.meanings", THAKSA_DECK.symbols, _SOURCE
)

__all__ = ["THAKSA_REGISTRY"]
