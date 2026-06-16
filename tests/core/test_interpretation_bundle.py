"""Schema validation and en-US derivation for locale translation bundles."""

from __future__ import annotations

import pytest
from fortune_telling_core.errors import ValidationError

from fortune_telling_core._interpretation_bundle import (
    SCHEMA_VERSION,
    LocaleBundle,
    _parse,
    americanize,
    load_bundle,
)

_ANCHOR = "fortune_telling_core.traditions.astrology.interpretation"


def _doc(**overrides: object) -> dict[str, object]:
    doc: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "locale": "fr-FR",
        "templates": {"placement": "x"},
        "vocab": {"signs": {"aries": "Bélier"}},
    }
    doc.update(overrides)
    return doc


def test_load_bundle_returns_validated_bundle() -> None:
    bundle = load_bundle(_ANCHOR, "signs", "fr-FR")
    assert bundle.locale == "fr-FR"
    assert bundle.template("placement")
    assert bundle.group("signs")["aries"] == "Bélier"


def test_missing_template_and_group_raise() -> None:
    bundle = load_bundle(_ANCHOR, "signs", "en-GB")
    with pytest.raises(ValidationError):
        bundle.template("does-not-exist")
    with pytest.raises(ValidationError):
        bundle.group("does-not-exist")


def test_missing_bundle_file_raises() -> None:
    with pytest.raises(ValidationError):
        load_bundle(_ANCHOR, "signs", "xx-XX")


@pytest.mark.parametrize(
    "overrides",
    [
        {"schema_version": 999},
        {"locale": "en-GB"},
        {"templates": ["not", "a", "map"]},
        {"vocab": {"signs": {"aries": 1}}},
        {"vocab": "not-a-map"},
    ],
)
def test_malformed_bundles_rejected(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        _parse(_doc(**overrides), "signs", "fr-FR")


def test_americanize_normalizes_british_spelling() -> None:
    en_gb = LocaleBundle(
        locale="en-GB",
        templates={"placement": "{body} in house {house} emphasises {topics}."},
        vocab={"text": {"a": "fulfilment and judgement", "b": "no change here"}},
    )
    en_us = americanize(en_gb)
    assert en_us.locale == "en-US"
    assert en_us.templates["placement"].endswith("emphasizes {topics}.")
    assert en_us.vocab["text"]["a"] == "fulfillment and judgment"
    assert en_us.vocab["text"]["b"] == "no change here"
