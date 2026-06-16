from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
    interpret,
)


def test_mapping_interpretation_lookup_fallback_chain() -> None:
    exact = InterpretationEntry(
        InterpretationKey("card", position_id="past", variant="upright"),
        "exact",
    )
    position_independent = InterpretationEntry(
        InterpretationKey("card", variant="upright"),
        "position independent",
    )
    variant_independent = InterpretationEntry(
        InterpretationKey("card", position_id="future"),
        "variant independent",
    )
    symbol_only = InterpretationEntry(InterpretationKey("card"), "symbol only")
    data = MappingInterpretationData(
        id="data",
        entries=(exact, position_independent, variant_independent, symbol_only),
    )

    assert data.lookup(InterpretationKey("card", "past", "upright")) == exact
    assert data.lookup(InterpretationKey("card", "present", "upright")) == position_independent
    assert data.lookup(InterpretationKey("card", "future", "reversed")) == variant_independent
    assert data.lookup(InterpretationKey("card", "present", "reversed")) == symbol_only
    assert data.lookup(InterpretationKey("other")) is None


def test_interpret_returns_position_mapping_for_structural_reading() -> None:
    from fortune_telling_core.draw import Draw, Selection
    from fortune_telling_core.spread import Spread
    from fortune_telling_core.symbols import Symbol

    from fortune_telling_core import Position, PositionReading, Provenance, Reading, ReadingRequest

    symbol = Symbol("card", "Card")
    position = Position("present", "Present")
    reading = Reading(
        request=ReadingRequest(deck_id="deck", spread_id="spread"),
        spread=Spread("spread", "Spread", (position,)),
        draw=Draw("deck", "spread", (Selection("present", "card"),)),
        positions=(PositionReading(position, symbol, Selection("present", "card")),),
        summary=None,
        provenance=Provenance("engine", "1", "core", "deck", "spread"),
        schema_version=1,
    )
    entry = InterpretationEntry(InterpretationKey("card"), "resolved")
    data = MappingInterpretationData("data", (entry,))

    assert interpret(reading, data) == {"present": entry}
