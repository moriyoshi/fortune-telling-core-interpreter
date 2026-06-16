"""Nine Star Ki star interpretation datasets across locales.

Translatable text lives in JSON bundles under ``locales/stars/<locale>.json``;
the stars and their CJK names come from core.
"""

from __future__ import annotations

from fortune_telling_core.traditions.nine_star_ki.stars import STARS

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core Nine Star Ki reference data, stars v1"
_ANCHOR = __name__.rpartition(".")[0]


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    element_line = bundle.template("element_line")
    natal_line = bundle.template("natal_line")
    colors = bundle.group("colors")
    elements = bundle.group("elements")
    trigrams = bundle.group("trigrams")
    return MappingInterpretationData(
        id=f"nsk.stars.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey(star.symbol_id, variant=star.element),
                element_line.format(
                    cjk=star.cjk,
                    color=colors[star.color],
                    element=elements[star.element],
                    trigram=trigrams[star.trigram],
                ),
                (star.element, star.color, star.trigram, star.slug),
                _SOURCE,
            )
            for star in STARS
        )
        + tuple(
            InterpretationEntry(
                InterpretationKey(star.symbol_id),
                natal_line.format(cjk=star.cjk),
                (star.element, star.color, star.slug),
                _SOURCE,
            )
            for star in STARS
        ),
    )


_DATASETS = build_all(_ANCHOR, "stars", _build)

STAR_EN_GB = _DATASETS["en-GB"]
STAR_EN_US = _DATASETS["en-US"]
STAR_FR_FR = _DATASETS["fr-FR"]
STAR_JA_JP = _DATASETS["ja-JP"]
STAR_REGISTRY = InterpretationRegistry(_DATASETS)
