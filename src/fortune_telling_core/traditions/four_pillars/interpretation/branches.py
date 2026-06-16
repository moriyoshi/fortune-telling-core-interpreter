"""Four Pillars earthly-branch interpretation datasets across locales.

Translatable text lives in JSON bundles under ``locales/branches/<locale>.json``;
the branches, their CJK glyphs, and English animal names come from core.
"""

from __future__ import annotations

from fortune_telling_core.traditions.four_pillars.stems_branches import BRANCHES

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core Four Pillars reference data, branches v1"
_ANCHOR = __name__.rpartition(".")[0]


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    template = bundle.template("branch")
    elements = bundle.group("elements")
    polarities = bundle.group("polarities")
    animals = bundle.group("animals")
    return MappingInterpretationData(
        id=f"fp.branches.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey(f"fp.branch.{branch.slug}"),
                template.format(
                    cjk=branch.cjk,
                    animal=animals[branch.animal],
                    polarity=polarities[branch.polarity.value],
                    element=elements[branch.element.value],
                ),
                (branch.element.value, branch.polarity.value, branch.animal.lower()),
                _SOURCE,
            )
            for branch in BRANCHES
        ),
    )


_DATASETS = build_all(_ANCHOR, "branches", _build)

BRANCH_EN_GB = _DATASETS["en-GB"]
BRANCH_EN_US = _DATASETS["en-US"]
BRANCH_FR_FR = _DATASETS["fr-FR"]
BRANCH_JA_JP = _DATASETS["ja-JP"]
BRANCH_REGISTRY = InterpretationRegistry(_DATASETS)
