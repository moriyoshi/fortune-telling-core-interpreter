"""Cyrillic Pythagorean numerology interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``CYRILLIC_PYTHAGOREAN_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.cyrillic_pythagorean import CYRILLIC_PYTHAGOREAN_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core cyrillic_pythagorean reference interpretation data v1"

CYRILLIC_PYTHAGOREAN_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "cyrillic_pythagorean.meanings", CYRILLIC_PYTHAGOREAN_DECK.symbols, _SOURCE
)

__all__ = ["CYRILLIC_PYTHAGOREAN_REGISTRY"]
