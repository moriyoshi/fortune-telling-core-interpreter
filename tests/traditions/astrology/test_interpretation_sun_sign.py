from datetime import UTC, datetime

from fortune_telling_core import Querent, ReadingRequest
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import interpret
from fortune_telling_core.traditions.astrology import (
    NATAL_CHART,
    SUN_SIGN,
    TROPICAL_ZODIAC,
    build_engine,
)
from fortune_telling_core.traditions.astrology.interpretation import ASTRO_SIGN_EN_GB

# The sun-sign spread reuses the natal ``sun`` position id, so the existing
# Sun-in-sign sign-placement dataset already covers it; no new interpretation
# data is needed. These tests lock that reuse in.
SIGN_REGISTRIES = (InterpretationRegistry({"en-GB": ASTRO_SIGN_EN_GB}),)


def _sun_sign_request(**attributes: str) -> ReadingRequest:
    return ReadingRequest(
        spread_id=SUN_SIGN.id,
        deck_id=TROPICAL_ZODIAC.id,
        querent=Querent(id="native", display_name="Native", attributes=attributes),
    )


def test_explicit_sun_sign_resolves_existing_sign_interpretation() -> None:
    reading = build_engine().cast(_sun_sign_request(sun_sign="leo"))

    entries = interpret(reading, SIGN_REGISTRIES, locale="en-GB")

    assert "sun" in entries
    assert entries["sun"].text == "Sun in Leo expresses through fire fixed qualities."


def test_birth_date_sun_sign_classified_into_sign_interpretation() -> None:
    # 1990-08-01 falls in Leo under the conventional tropical date ranges.
    reading = build_engine().cast(_sun_sign_request(birth_date="1990-08-01"))

    entries = interpret(reading, SIGN_REGISTRIES, locale="en-GB")

    assert entries["sun"].text == "Sun in Leo expresses through fire fixed qualities."


def test_sun_sign_text_matches_natal_chart_sun_placement() -> None:
    # The whole point of reusing the ``sun`` position id is that the lightweight
    # sun-sign reading yields the same Sun-in-sign text as a full natal chart.
    natal = build_engine().cast(
        ReadingRequest(
            spread_id=NATAL_CHART.id,
            deck_id=TROPICAL_ZODIAC.id,
            querent=Querent(
                id="native",
                display_name="Native",
                attributes={
                    "birth_datetime": datetime(1990, 8, 1, 12, tzinfo=UTC).isoformat(),
                    "latitude": "0",
                    "longitude": "0",
                    "house_system": "whole_sign",
                },
            ),
        )
    )
    sun_sign = build_engine().cast(_sun_sign_request(birth_date="1990-08-01"))

    natal_entries = interpret(natal, SIGN_REGISTRIES, locale="en-GB")
    sun_sign_entries = interpret(sun_sign, SIGN_REGISTRIES, locale="en-GB")

    assert sun_sign_entries["sun"].text == natal_entries["sun"].text
