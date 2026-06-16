"""Astrology sign-placement interpretation datasets across locales.

Translatable text (templates and vocabulary) lives in JSON bundles under
``locales/signs/<locale>.json``; see :mod:`fortune_telling_core._interpretation_bundle`.
The set of signs and their order come from core's ``Sign`` enum, the single
source of truth for the zodiac, so the builder joins each bundle's strings with
that structural data. en-US is derived from en-GB by spelling normalization.
"""

from __future__ import annotations

from fortune_telling_core.traditions.astrology.bodies import NATAL_POSITIONS

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)
from fortune_telling_core.traditions.astrology import TROPICAL_ZODIAC, Sign

_SOURCE = "fortune-telling-core astrology reference data, sign placements v1"
_ANCHOR = __name__.rpartition(".")[0]

# Sign attributes (element, modality) live on the zodiac deck symbols.
_SYMBOLS_BY_ID = {symbol.id: symbol for symbol in TROPICAL_ZODIAC.symbols}


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    placement = bundle.template("placement")
    retrograde_suffix = bundle.template("retrograde_suffix")
    signs = bundle.group("signs")
    bodies = bundle.group("bodies")
    elements = bundle.group("elements")
    modalities = bundle.group("modalities")
    entries: list[InterpretationEntry] = []
    for sign in Sign:
        symbol = _SYMBOLS_BY_ID[sign.symbol_id]
        element = symbol.attributes["element"]
        modality = symbol.attributes["modality"]
        sign_name = signs[sign.value]
        element_disp = elements[element]
        modality_disp = modalities[modality]
        # Keywords stay on stable, language-neutral tokens so search behaves the
        # same across locales.
        base_keywords = (sign.value, element, modality)
        for position_id in NATAL_POSITIONS:
            body_name = bodies[position_id]
            text = placement.format(
                body=body_name,
                sign=sign_name,
                element=element_disp,
                modality=modality_disp,
            )
            entries.append(
                InterpretationEntry(
                    key=InterpretationKey(symbol_id=sign.symbol_id, position_id=position_id),
                    text=text,
                    keywords=(*base_keywords, position_id),
                    source=_SOURCE,
                )
            )
            entries.append(
                InterpretationEntry(
                    key=InterpretationKey(
                        symbol_id=sign.symbol_id,
                        position_id=position_id,
                        variant="retrograde",
                    ),
                    text=f"{text}{retrograde_suffix}",
                    keywords=(*base_keywords, position_id, "retrograde"),
                    source=_SOURCE,
                )
            )
    return MappingInterpretationData(id=f"astro.signs.{locale}.v1", entries=tuple(entries))


_DATASETS = build_all(_ANCHOR, "signs", _build)

ASTRO_SIGN_EN_GB = _DATASETS["en-GB"]
ASTRO_SIGN_EN_US = _DATASETS["en-US"]
ASTRO_SIGN_FR_FR = _DATASETS["fr-FR"]
ASTRO_SIGN_JA_JP = _DATASETS["ja-JP"]
ASTRO_SIGN_REGISTRY = InterpretationRegistry(_DATASETS)
