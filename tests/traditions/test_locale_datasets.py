"""Cross-locale coverage and registry resolution for template datasets."""

from __future__ import annotations

import pytest

from fortune_telling_core._interpretation_bundle import load_bundle
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import InterpretationKey, MappingInterpretationData
from fortune_telling_core.traditions.astrology import Sign
from fortune_telling_core.traditions.astrology.interpretation import (
    ASTRO_ASPECT_REGISTRY,
    ASTRO_HOUSE_EN_GB,
    ASTRO_HOUSE_EN_US,
    ASTRO_HOUSE_REGISTRY,
    ASTRO_SIGN_REGISTRY,
)
from fortune_telling_core.traditions.cjk_name_strokes.interpretation import (
    STROKE_COUNT_REGISTRIES,
)
from fortune_telling_core.traditions.four_pillars.interpretation import (
    BRANCH_REGISTRY,
    STEM_REGISTRY,
    TEN_GODS_REGISTRY,
)
from fortune_telling_core.traditions.nine_star_ki.interpretation import (
    POSITION_REGISTRY,
    STAR_REGISTRY,
)
from fortune_telling_core.traditions.tarot.interpretation import (
    RWS_EN_GB,
    RWS_EN_US,
    RWS_REGISTRY,
)

_SIGN_ANCHOR = "fortune_telling_core.traditions.astrology.interpretation"

# The four locales with named module-level constants and authored/derived text
# guaranteed present everywhere.
LOCALES = ("en-GB", "en-US", "fr-FR", "ja-JP")
# All locales that ship a bundle for every family (authored fr-FR/ja-JP and the
# dispatched set), plus the derived en-US.
ALL_LOCALES = (
    "en-GB",
    "en-US",
    "fr-FR",
    "de-DE",
    "ja-JP",
    "zh-CN",
    "zh-TW",
    "pt-BR",
    "es-ES",
    "ru-RU",
    "id-ID",
    "vi-VN",
    "th-TH",
    "hi-IN",
    "bn-IN",
    "te-IN",
    "mr-IN",
    "ta-IN",
)
REGISTRIES = (
    ASTRO_SIGN_REGISTRY,
    ASTRO_HOUSE_REGISTRY,
    ASTRO_ASPECT_REGISTRY,
    STEM_REGISTRY,
    BRANCH_REGISTRY,
    TEN_GODS_REGISTRY,
    STAR_REGISTRY,
    POSITION_REGISTRY,
    RWS_REGISTRY,
    *STROKE_COUNT_REGISTRIES.values(),
)


def _datasets(registry: InterpretationRegistry) -> dict[str, MappingInterpretationData]:
    resolved: dict[str, MappingInterpretationData] = {}
    for locale in LOCALES:
        data = registry.lookup(locale).data
        assert isinstance(data, MappingInterpretationData)
        resolved[locale] = data
    return resolved


@pytest.mark.parametrize("registry", REGISTRIES)
def test_registry_resolves_every_locale_to_its_own_dataset(
    registry: InterpretationRegistry,
) -> None:
    for locale in LOCALES:
        lookup = registry.lookup(locale)
        assert lookup.resolved_locale == locale
        assert lookup.data is not None
        assert lookup.data.id.split(".")[-2] == locale


@pytest.mark.parametrize("registry", REGISTRIES)
def test_every_locale_covers_the_same_keys_and_sources(
    registry: InterpretationRegistry,
) -> None:
    datasets = _datasets(registry)
    reference = datasets["en-GB"]
    reference_keys = {entry.key for entry in reference.entries}
    reference_sources = {entry.source for entry in reference.entries}
    for locale, data in datasets.items():
        assert {entry.key for entry in data.entries} == reference_keys, locale
        # The provenance string is dataset identity and is shared verbatim.
        assert {entry.source for entry in data.entries} == reference_sources, locale


@pytest.mark.parametrize("registry", REGISTRIES)
def test_all_locales_present_and_structurally_consistent(
    registry: InterpretationRegistry,
) -> None:
    # Every advertised locale must resolve, and every locale's dataset must cover
    # exactly the en-GB lookup keys with the shared source string. This guards the
    # full externalized bundle set, including the dispatched translations.
    en_gb = registry.lookup("en-GB").data
    assert isinstance(en_gb, MappingInterpretationData)
    reference_keys = {entry.key for entry in en_gb.entries}
    reference_sources = {entry.source for entry in en_gb.entries}
    for locale in ALL_LOCALES:
        data = registry.lookup(locale).data
        assert isinstance(data, MappingInterpretationData), locale
        assert {entry.key for entry in data.entries} == reference_keys, locale
        assert {entry.source for entry in data.entries} == reference_sources, locale
        assert all(entry.text.strip() for entry in data.entries), locale


@pytest.mark.parametrize("registry", REGISTRIES)
def test_localized_text_differs_from_english(registry: InterpretationRegistry) -> None:
    datasets = _datasets(registry)
    en_text = {entry.key: entry.text for entry in datasets["en-GB"].entries}
    for locale in ("fr-FR", "ja-JP"):
        localized = {entry.key: entry.text for entry in datasets[locale].entries}
        assert all(localized[key] != en_text[key] for key in en_text), locale


def test_registry_normalizes_locale_tags() -> None:
    # en_US -> en-US resolves to the en-US dataset directly (no fallback).
    lookup = STEM_REGISTRY.lookup("en_us")
    assert lookup.normalized_locale == "en-US"
    assert lookup.resolved_locale == "en-US"
    assert lookup.data is STEM_REGISTRY.datasets["en-US"]


def test_unsupported_locale_returns_no_dataset() -> None:
    lookup = STAR_REGISTRY.lookup("xx-XX")
    assert lookup.data is None
    assert "resolved_locale=xx-XX" in lookup.provenance_notes


def test_en_us_house_dataset_overrides_british_spelling() -> None:
    gb = {entry.key: entry.text for entry in ASTRO_HOUSE_EN_GB.entries}
    us = {entry.key: entry.text for entry in ASTRO_HOUSE_EN_US.entries}
    sample = InterpretationKey(symbol_id="astro.house.1", position_id="sun")
    assert "emphasises" in gb[sample]
    assert "emphasizes" in us[sample]


def test_rws_tarot_localized_into_four_locales_with_same_cards() -> None:
    datasets = _datasets(RWS_REGISTRY)
    reference_keys = {entry.key for entry in datasets["en-GB"].entries}
    assert len(reference_keys) == 78 * 3
    for locale, data in datasets.items():
        assert {entry.key for entry in data.entries} == reference_keys, locale
        assert all("Pictorial Key" in entry.source for entry in data.entries if entry.source)


def test_en_us_tarot_normalizes_british_spelling() -> None:
    key = InterpretationKey(symbol_id="tarot.rws.major.the_emperor")
    gb = RWS_EN_GB.lookup(key)
    us = RWS_EN_US.lookup(key)
    assert gb is not None and us is not None
    assert "stabilise" in gb.text
    assert "stabilize" in us.text


def test_japanese_tarot_renders_japanese_text() -> None:
    data = RWS_REGISTRY.lookup("ja-JP").data
    assert data is not None
    entry = data.lookup(InterpretationKey(symbol_id="tarot.rws.major.the_fool", variant="reversed"))
    assert entry is not None
    assert any("぀" <= ch <= "ヿ" or "一" <= ch <= "鿿" for ch in entry.text)


def test_sign_datasets_track_core_sign_enum() -> None:
    # Core's Sign enum is the single source of truth for the zodiac; the sign
    # datasets and every localized name map must cover exactly its members.
    expected_symbol_ids = {sign.symbol_id for sign in Sign}
    expected_slugs = {sign.value for sign in Sign}
    for locale, data in _datasets(ASTRO_SIGN_REGISTRY).items():
        covered = {entry.key.symbol_id for entry in data.entries}
        assert covered == expected_symbol_ids, locale
    # Every authored bundle must name every sign in core's enum.
    for locale in ("en-GB", "fr-FR", "ja-JP"):
        bundle = load_bundle(_SIGN_ANCHOR, "signs", locale)
        assert set(bundle.group("signs")) == expected_slugs, locale


def test_japanese_sign_interpretation_renders_localized_terms() -> None:
    data = ASTRO_SIGN_REGISTRY.lookup("ja-JP").data
    assert data is not None
    entry = data.lookup(InterpretationKey(symbol_id="astro.sign.aries", position_id="sun"))
    assert entry is not None
    assert "牡羊座" in entry.text
    assert "太陽" in entry.text
