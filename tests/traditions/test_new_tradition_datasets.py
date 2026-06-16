"""Structural checks for the symbol-keyed new-tradition interpretation datasets."""

from __future__ import annotations

import pytest

from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import MappingInterpretationData
from fortune_telling_core.traditions.can_chi.interpretation import CAN_CHI_REGISTRY
from fortune_telling_core.traditions.celtic_tree.interpretation import CELTIC_TREE_REGISTRY
from fortune_telling_core.traditions.chaldean_numerology.interpretation import (
    CHALDEAN_NUMEROLOGY_REGISTRY,
)
from fortune_telling_core.traditions.cjk_name_strokes.interpretation import (
    CJK_NAME_STROKES_REGISTRY,
)
from fortune_telling_core.traditions.cyrillic_pythagorean.interpretation import (
    CYRILLIC_PYTHAGOREAN_REGISTRY,
)
from fortune_telling_core.traditions.cyrillic_slavonic_numerals.interpretation import (
    CYRILLIC_SLAVONIC_NUMERALS_REGISTRY,
)
from fortune_telling_core.traditions.dominoes.interpretation import DOMINOES_REGISTRY
from fortune_telling_core.traditions.geomancy.interpretation import GEOMANCY_REGISTRY
from fortune_telling_core.traditions.greek_isopsephy.interpretation import GREEK_ISOPSEPHY_REGISTRY
from fortune_telling_core.traditions.haab.interpretation import HAAB_REGISTRY
from fortune_telling_core.traditions.iching.interpretation import ICHING_REGISTRY
from fortune_telling_core.traditions.koyomi.interpretation import KOYOMI_REGISTRY
from fortune_telling_core.traditions.lenormand.interpretation import LENORMAND_REGISTRY
from fortune_telling_core.traditions.name_numerology.interpretation import NAME_NUMEROLOGY_REGISTRY
from fortune_telling_core.traditions.numerology.interpretation import NUMEROLOGY_REGISTRY
from fortune_telling_core.traditions.runes.interpretation import RUNES_REGISTRY
from fortune_telling_core.traditions.sanmeigaku.interpretation import SANMEIGAKU_REGISTRY
from fortune_telling_core.traditions.sukuyo.interpretation import SUKUYO_REGISTRY
from fortune_telling_core.traditions.thaksa.interpretation import THAKSA_REGISTRY
from fortune_telling_core.traditions.tzolkin.interpretation import TZOLKIN_REGISTRY
from fortune_telling_core.traditions.weton.interpretation import WETON_REGISTRY
from fortune_telling_core.traditions.zi_wei.interpretation import ZI_WEI_PALACE_REGISTRY

NEW_REGISTRIES = (
    CAN_CHI_REGISTRY,
    CELTIC_TREE_REGISTRY,
    CHALDEAN_NUMEROLOGY_REGISTRY,
    CJK_NAME_STROKES_REGISTRY,
    CYRILLIC_PYTHAGOREAN_REGISTRY,
    CYRILLIC_SLAVONIC_NUMERALS_REGISTRY,
    DOMINOES_REGISTRY,
    GEOMANCY_REGISTRY,
    GREEK_ISOPSEPHY_REGISTRY,
    HAAB_REGISTRY,
    ICHING_REGISTRY,
    KOYOMI_REGISTRY,
    LENORMAND_REGISTRY,
    NAME_NUMEROLOGY_REGISTRY,
    NUMEROLOGY_REGISTRY,
    RUNES_REGISTRY,
    SANMEIGAKU_REGISTRY,
    SUKUYO_REGISTRY,
    THAKSA_REGISTRY,
    TZOLKIN_REGISTRY,
    WETON_REGISTRY,
    ZI_WEI_PALACE_REGISTRY,
)


@pytest.mark.parametrize("registry", NEW_REGISTRIES)
def test_en_gb_and_derived_en_us_present(registry: InterpretationRegistry) -> None:
    for locale in ("en-GB", "en-US"):
        data = registry.lookup(locale).data
        assert isinstance(data, MappingInterpretationData), locale
        assert data.entries
        assert all(entry.text.strip() for entry in data.entries), locale
        assert all(entry.source for entry in data.entries), locale


@pytest.mark.parametrize("registry", NEW_REGISTRIES)
def test_every_locale_matches_en_gb_keys(registry: InterpretationRegistry) -> None:
    en_gb = registry.lookup("en-GB").data
    assert isinstance(en_gb, MappingInterpretationData)
    reference_keys = {entry.key for entry in en_gb.entries}
    for locale, data in registry.datasets.items():
        assert isinstance(data, MappingInterpretationData), locale
        assert {entry.key for entry in data.entries} == reference_keys, locale
    # en-US is derived and must also match.
    us = registry.lookup("en-US").data
    assert isinstance(us, MappingInterpretationData)
    assert {entry.key for entry in us.entries} == reference_keys
