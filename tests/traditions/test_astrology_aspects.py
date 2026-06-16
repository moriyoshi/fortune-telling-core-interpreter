"""Astrology aspect interpretation: off-grid extras resolved via interpret_extras."""

from __future__ import annotations

from fortune_telling_core.draw import Draw, Selection
from fortune_telling_core.spread import Spread
from fortune_telling_core.symbols import Symbol

from fortune_telling_core import (
    Position,
    PositionReading,
    Provenance,
    Reading,
    ReadingRequest,
)
from fortune_telling_core.interpretation import (
    MappingInterpretationData,
    interpret,
    interpret_extras,
)
from fortune_telling_core.traditions.astrology.interpretation import ASTRO_ASPECT_REGISTRY

_ASPECTS = ("conjunction", "opposition", "trine", "square", "sextile")


def _reading_with_aspects(*extras: Selection) -> Reading:
    symbol = Symbol("astro.body.sun", "Sun")
    position = Position("sun", "Sun")
    selection = Selection("sun", symbol.id, {"longitude": "54.0"})
    return Reading(
        request=ReadingRequest(deck_id="deck", spread_id="spread"),
        spread=Spread("spread", "Spread", (position,)),
        draw=Draw("deck", "spread", (selection,), extras=extras),
        positions=(PositionReading(position, symbol, selection),),
        summary=None,
        provenance=Provenance("engine", "1", "core", "deck", "spread"),
        schema_version=1,
    )


def _aspect(aspect_type: str, first: str, second: str, kind: str) -> Selection:
    return Selection(
        "aspect",
        f"astro.aspect.{aspect_type}",
        {"first": first, "second": second, "orb": "1.50", "kind": kind},
    )


def test_aspect_dataset_covers_the_five_types() -> None:
    for locale in ("en-GB", "en-US"):
        data = ASTRO_ASPECT_REGISTRY.lookup(locale).data
        assert isinstance(data, MappingInterpretationData), locale
        ids = {entry.key.symbol_id for entry in data.entries}
        assert ids == {f"astro.aspect.{a}" for a in _ASPECTS}, locale
        assert all(entry.text.strip() for entry in data.entries), locale


def test_interpret_extras_resolves_natal_and_transit_aspects() -> None:
    reading = _reading_with_aspects(
        _aspect("trine", "sun", "moon", "natal"),
        _aspect("conjunction", "sun", "mars", "transit"),
    )
    resolved = interpret_extras(reading, ASTRO_ASPECT_REGISTRY, locale="en-GB")
    assert len(resolved) == 2
    (sel0, e0), (sel1, e1) = resolved
    assert e0 is not None and "trine" in e0.text
    assert e1 is not None and "conjunction" in e1.text
    assert (sel0.modifiers or {})["kind"] == "natal"
    assert (sel1.modifiers or {})["kind"] == "transit"


def test_interpret_ignores_extras_and_interpret_extras_ignores_positions() -> None:
    # The position-keyed path never picks up aspects, and vice versa.
    reading = _reading_with_aspects(_aspect("square", "venus", "mars", "natal"))
    assert "aspect" not in interpret(reading, ASTRO_ASPECT_REGISTRY)
    assert len(interpret_extras(reading, ASTRO_ASPECT_REGISTRY)) == 1


def test_reading_without_extras_yields_no_aspect_interpretations() -> None:
    reading = _reading_with_aspects()  # no extras
    assert interpret_extras(reading, ASTRO_ASPECT_REGISTRY) == []
