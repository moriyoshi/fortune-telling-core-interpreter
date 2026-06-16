"""Sukuyō (宿曜) lunar-mansion interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the twenty-seven mansion symbols come from core's ``SUKUYO_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.sukuyo import SUKUYO_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core sukuyo reference interpretation data v1"

SUKUYO_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "sukuyo.meanings", SUKUYO_DECK.symbols, _SOURCE
)

__all__ = ["SUKUYO_REGISTRY"]
