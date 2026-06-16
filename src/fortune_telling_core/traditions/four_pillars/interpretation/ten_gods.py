"""Four Pillars Ten Gods interpretation datasets across locales.

Translatable text lives in JSON bundles under ``locales/ten_gods/<locale>.json``;
the stems and the set of Ten Gods come from core.
"""

from __future__ import annotations

from fortune_telling_core.traditions.four_pillars.stems_branches import STEMS
from fortune_telling_core.traditions.four_pillars.ten_gods import TEN_GOD_LABELS

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core Four Pillars reference data, Ten Gods v1"
_ANCHOR = __name__.rpartition(".")[0]


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    template = bundle.template("ten_god")
    labels = bundle.group("labels")
    return MappingInterpretationData(
        id=f"fp.tengods.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey(f"fp.stem.{stem.slug}", variant=god),
                template.format(label=labels[god]),
                (god, stem.element.value, stem.polarity.value),
                _SOURCE,
            )
            for stem in STEMS
            for god in TEN_GOD_LABELS
        ),
    )


_DATASETS = build_all(_ANCHOR, "ten_gods", _build)

TEN_GODS_EN_GB = _DATASETS["en-GB"]
TEN_GODS_EN_US = _DATASETS["en-US"]
TEN_GODS_FR_FR = _DATASETS["fr-FR"]
TEN_GODS_JA_JP = _DATASETS["ja-JP"]
TEN_GODS_REGISTRY = InterpretationRegistry(_DATASETS)
