"""Celtic tree (Ogham tree zodiac) interpretation datasets across locales.

Per-symbol meaning text lives in JSON bundles under ``locales/meanings/<locale>.json``;
the symbols come from core's ``CELTIC_TREE_DECK``. See
:mod:`fortune_telling_core._symbol_interpretation` and
:mod:`fortune_telling_core._interpretation_bundle`.
"""

from fortune_telling_core._symbol_interpretation import symbol_registry
from fortune_telling_core.traditions.celtic_tree import CELTIC_TREE_DECK

_ANCHOR = __name__
_SOURCE = "fortune-telling-core celtic_tree reference interpretation data v1"

CELTIC_TREE_REGISTRY = symbol_registry(
    _ANCHOR, "meanings", "celtic_tree.meanings", CELTIC_TREE_DECK.symbols, _SOURCE
)

__all__ = ["CELTIC_TREE_REGISTRY"]
