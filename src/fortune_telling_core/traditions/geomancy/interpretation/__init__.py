"""Western geomancy interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``GEOMANCY_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.geomancy import GEOMANCY_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core geomancy reference interpretation data v1"

GEOMANCY_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "geomancy.meanings", GEOMANCY_DECK.symbols, _SOURCE
)

__all__ = ["GEOMANCY_REGISTRY"]
