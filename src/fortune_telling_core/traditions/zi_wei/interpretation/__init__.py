"""Zi Wei Dou Shu (紫微斗数) palace interpretation datasets across locales.

A Zi Wei chart assigns the twelve palaces (命宮, 兄弟宮, …) to earthly branches;
the substantive reading is per-palace, so interpretation is keyed by the spread's
palace ``position_id`` rather than by the branch deck symbol. Palace text lives in
JSON bundles under ``locales/palaces/<locale>.json`` as the ``texts`` vocab group
(keyed by palace id); there is no template. See
:func:`fortune_telling_core.interpretation._candidate_keys` for the lookup side
(the ``zi_wei.palace`` key) and :mod:`fortune_telling_core._interpretation_bundle`.
"""

from __future__ import annotations

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core zi_wei reference interpretation data, palaces v1"
_ANCHOR = __name__


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    texts = bundle.group("texts")
    return MappingInterpretationData(
        id=f"zi_wei.palaces.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey("zi_wei.palace", position_id=palace_id),
                text,
                (palace_id,),
                _SOURCE,
            )
            for palace_id, text in texts.items()
        ),
    )


_DATASETS = build_all(_ANCHOR, "palaces", _build)

ZI_WEI_PALACE_EN_GB = _DATASETS["en-GB"]
ZI_WEI_PALACE_EN_US = _DATASETS["en-US"]
ZI_WEI_PALACE_REGISTRY = InterpretationRegistry(_DATASETS)

__all__ = [
    "ZI_WEI_PALACE_EN_GB",
    "ZI_WEI_PALACE_EN_US",
    "ZI_WEI_PALACE_REGISTRY",
]
