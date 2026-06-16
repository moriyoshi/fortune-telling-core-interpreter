"""Astrology house-placement interpretation datasets across locales.

Translatable text lives in JSON bundles under ``locales/houses/<locale>.json``.
The house numbers and the language-neutral topic slugs that drive keyword tokens
stay in code; the bundle supplies the localized topic phrases and template.
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

_SOURCE = "fortune-telling-core astrology reference data, house placements v1"
_ANCHOR = __name__.rpartition(".")[0]

# Stable, language-neutral topic slugs. These drive the keyword tokens for every
# locale; the localized display phrases live in each bundle's ``topics`` group.
_HOUSE_TOPICS: dict[int, tuple[str, ...]] = {
    1: ("identity", "body", "approach"),
    2: ("resources", "values", "security"),
    3: ("communication", "siblings", "learning"),
    4: ("home", "roots", "private-life"),
    5: ("creativity", "pleasure", "children"),
    6: ("work", "health", "service"),
    7: ("partnership", "contracts", "others"),
    8: ("shared-resources", "loss", "transformation"),
    9: ("belief", "travel", "higher-learning"),
    10: ("vocation", "status", "public-life"),
    11: ("friends", "hopes", "groups"),
    12: ("retreat", "hidden-matters", "self-undoing"),
}


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    placement = bundle.template("placement")
    bodies = bundle.group("bodies")
    topics = bundle.group("topics")
    entries: list[InterpretationEntry] = []
    for house_number, topic_slugs in _HOUSE_TOPICS.items():
        symbol_id = f"astro.house.{house_number}"
        topic_text = topics[str(house_number)]
        base_keywords = (f"house-{house_number}", *topic_slugs)
        for position_id in NATAL_POSITIONS:
            body_name = bodies[position_id]
            text = placement.format(body=body_name, house=house_number, topics=topic_text)
            entries.append(
                InterpretationEntry(
                    key=InterpretationKey(symbol_id=symbol_id, position_id=position_id),
                    text=text,
                    keywords=(*base_keywords, position_id),
                    source=_SOURCE,
                )
            )
    return MappingInterpretationData(id=f"astro.houses.{locale}.v1", entries=tuple(entries))


_DATASETS = build_all(_ANCHOR, "houses", _build)

ASTRO_HOUSE_EN_GB = _DATASETS["en-GB"]
ASTRO_HOUSE_EN_US = _DATASETS["en-US"]
ASTRO_HOUSE_FR_FR = _DATASETS["fr-FR"]
ASTRO_HOUSE_JA_JP = _DATASETS["ja-JP"]
ASTRO_HOUSE_REGISTRY = InterpretationRegistry(_DATASETS)
