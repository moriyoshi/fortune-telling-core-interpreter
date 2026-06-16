"""Pythagorean name numerology interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``NAME_NUMEROLOGY_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.name_numerology import NAME_NUMEROLOGY_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core name_numerology reference interpretation data v1"

NAME_NUMEROLOGY_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "name_numerology.meanings", NAME_NUMEROLOGY_DECK.symbols, _SOURCE
)

__all__ = ["NAME_NUMEROLOGY_REGISTRY"]
