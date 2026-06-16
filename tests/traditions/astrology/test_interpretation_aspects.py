from datetime import UTC, datetime

from fortune_telling_core.traditions.astrology.aspects import compute_aspects
from fortune_telling_core.traditions.astrology.bodies import Body
from fortune_telling_core.traditions.astrology.positions import EclipticPosition

from fortune_telling_core import Querent, ReadingRequest
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import interpret
from fortune_telling_core.traditions.astrology import (
    NATAL_CHART,
    TROPICAL_ZODIAC,
    FixedEphemeris,
    build_engine,
)
from fortune_telling_core.traditions.astrology.interpretation import (
    ASTRO_HOUSE_EN_GB,
    ASTRO_SIGN_EN_GB,
)

ASTRO_REGISTRIES = (
    InterpretationRegistry({"en-GB": ASTRO_SIGN_EN_GB}),
    InterpretationRegistry({"en-GB": ASTRO_HOUSE_EN_GB}),
)


def test_composes_sign_house_and_retrograde_interpretation() -> None:
    reading = build_engine(
        FixedEphemeris(
            {
                Body.SUN: EclipticPosition(10.0, 1.0),
                Body.MOON: EclipticPosition(40.0, 1.0),
                Body.MERCURY: EclipticPosition(70.0, -1.0),
                Body.VENUS: EclipticPosition(100.0, 1.0),
                Body.MARS: EclipticPosition(130.0, 1.0),
                Body.JUPITER: EclipticPosition(160.0, 1.0),
                Body.SATURN: EclipticPosition(190.0, 1.0),
                Body.URANUS: EclipticPosition(220.0, 1.0),
                Body.NEPTUNE: EclipticPosition(250.0, 1.0),
                Body.PLUTO: EclipticPosition(280.0, 1.0),
                Body.NORTH_NODE: EclipticPosition(310.0, -0.1),
            }
        )
    ).cast(_request())

    mercury = next(
        position for position in reading.positions if position.selection.position_id == "mercury"
    )
    entries = interpret(reading, ASTRO_REGISTRIES, locale="en-GB")

    assert mercury.selection.position_id in entries
    assert "Retrograde motion" in entries["mercury"].text
    assert "house" in entries["mercury"].text


def test_aspects_orbs_and_node_opposition_suppression() -> None:
    aspects = compute_aspects(
        {"sun": 0.0, "moon": 1.0, "mars": 90.0, "north_node": 10.0, "south_node": 190.0}
    )

    rendered = [aspect.render() for aspect in aspects]
    assert any("sun conjunct moon" in item for item in rendered)
    assert any("sun squares mars" in item for item in rendered)
    assert not any("north_node opposes south_node" in item for item in rendered)


def _request() -> ReadingRequest:
    return ReadingRequest(
        spread_id=NATAL_CHART.id,
        deck_id=TROPICAL_ZODIAC.id,
        querent=Querent(
            id="native",
            display_name="Native",
            attributes={
                "birth_datetime": datetime(1990, 1, 1, 12, tzinfo=UTC).isoformat(),
                "latitude": "0",
                "longitude": "0",
                "house_system": "whole_sign",
            },
        ),
    )
