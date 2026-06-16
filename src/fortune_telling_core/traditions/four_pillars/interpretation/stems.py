"""Four Pillars heavenly-stem interpretation datasets across locales.

Translatable text lives in JSON bundles under ``locales/stems/<locale>.json``;
the stems and their CJK glyphs come from core. en-US is derived from en-GB.
"""

from __future__ import annotations

from fortune_telling_core.traditions.four_pillars.stems_branches import STEMS

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core Four Pillars reference data, stems v1"
_ANCHOR = __name__.rpartition(".")[0]


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    template = bundle.template("stem")
    elements = bundle.group("elements")
    polarities = bundle.group("polarities")
    return MappingInterpretationData(
        id=f"fp.stems.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey(f"fp.stem.{stem.slug}"),
                template.format(
                    cjk=stem.cjk,
                    polarity=polarities[stem.polarity.value],
                    element=elements[stem.element.value],
                ),
                (stem.element.value, stem.polarity.value, stem.slug),
                _SOURCE,
            )
            for stem in STEMS
        ),
    )


_DATASETS = build_all(_ANCHOR, "stems", _build)

STEM_EN_GB = _DATASETS["en-GB"]
STEM_EN_US = _DATASETS["en-US"]
STEM_FR_FR = _DATASETS["fr-FR"]
STEM_JA_JP = _DATASETS["ja-JP"]
STEM_REGISTRY = InterpretationRegistry(_DATASETS)
