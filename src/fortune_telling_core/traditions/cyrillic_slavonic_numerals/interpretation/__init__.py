"""Old Cyrillic / Church Slavonic numeral interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``CYRILLIC_SLAVONIC_NUMERALS_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.cyrillic_slavonic_numerals import (
    CYRILLIC_SLAVONIC_NUMERALS_DECK,
)

_ANCHOR = __name__
_SOURCE = "fortune-telling-core cyrillic_slavonic_numerals reference interpretation data v1"

CYRILLIC_SLAVONIC_NUMERALS_REGISTRY = symbol_registry(
    _ANCHOR,
    "meanings",
    "cyrillic_slavonic_numerals.meanings",
    CYRILLIC_SLAVONIC_NUMERALS_DECK.symbols,
    _SOURCE,
)

__all__ = ["CYRILLIC_SLAVONIC_NUMERALS_REGISTRY"]
