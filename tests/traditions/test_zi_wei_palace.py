"""Zi Wei Dou Shu: palace interpretation keyed by spread position, not branch."""

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
from fortune_telling_core.interpretation import MappingInterpretationData, interpret
from fortune_telling_core.traditions.zi_wei.interpretation import ZI_WEI_PALACE_REGISTRY


def _palace_reading(position_id: str, branch_id: str) -> Reading:
    """A one-position reading: the given palace landing on the given branch."""

    symbol = Symbol(branch_id, branch_id, attributes={"cjk": "子", "index": "0"})
    position = Position(position_id, position_id)
    selection = Selection(position_id, symbol.id, {"palace": "命宮"})
    return Reading(
        request=ReadingRequest(deck_id="deck", spread_id="spread"),
        spread=Spread("spread", "Spread", (position,)),
        draw=Draw("deck", "spread", (selection,)),
        positions=(PositionReading(position, symbol, selection),),
        summary=None,
        provenance=Provenance("engine", "1", "core", "deck", "spread"),
        schema_version=1,
    )


def test_palace_text_keyed_by_position_not_branch() -> None:
    # Same branch symbol, two different palaces -> two different readings.
    ming = interpret(_palace_reading("ming", "zi_wei.branch.zi"), ZI_WEI_PALACE_REGISTRY)
    wealth = interpret(_palace_reading("wealth", "zi_wei.branch.zi"), ZI_WEI_PALACE_REGISTRY)
    assert "Life Palace" in ming["ming"].text
    assert "Wealth Palace" in wealth["wealth"].text
    assert ming["ming"].text != wealth["wealth"].text


def test_palace_dataset_covers_the_twelve_palaces() -> None:
    data = ZI_WEI_PALACE_REGISTRY.lookup("en-GB").data
    assert isinstance(data, MappingInterpretationData)
    palaces = {entry.key.position_id for entry in data.entries}
    assert palaces == {
        "ming",
        "siblings",
        "spouse",
        "children",
        "wealth",
        "health",
        "travel",
        "friends",
        "career",
        "property",
        "fortune",
        "parents",
    }
    assert all(entry.key.symbol_id == "zi_wei.palace" for entry in data.entries)
