from fortune_telling_core import ReadingRequest, SequenceRng
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import interpret
from fortune_telling_core.traditions.tarot import RWS_DECK, SINGLE_CARD, build_engine
from fortune_telling_core.traditions.tarot.interpretation import RWS_EN_GB

RWS_REGISTRY = InterpretationRegistry({"en-GB": RWS_EN_GB})


def test_rws_interpretation_data_covers_base_upright_and_reversed_with_sources() -> None:
    assert len(RWS_EN_GB.entries) == 78 * 3
    assert all(
        entry.source is not None and "Pictorial Key" in entry.source for entry in RWS_EN_GB.entries
    )
    assert all(entry.key.variant in {None, "upright", "reversed"} for entry in RWS_EN_GB.entries)
    assert all(
        entry.key.symbol_id in {symbol.id for symbol in RWS_DECK.symbols}
        for entry in RWS_EN_GB.entries
    )


def test_every_reachable_single_card_selection_resolves_to_entry() -> None:
    engine = build_engine()

    for index, symbol in enumerate(RWS_DECK.symbols):
        order = [index, *(item for item in range(78) if item != index)]
        for allow_reversals, floats in ((False, []), (True, [0.1]), (True, [0.9])):
            request = ReadingRequest(
                spread_id=SINGLE_CARD.id,
                deck_id=RWS_DECK.id,
                options={"allow_reversals": "true"} if allow_reversals else {},
            )
            reading = engine.read(request, rng=SequenceRng(ints=order, floats=floats))
            entries = interpret(reading, RWS_REGISTRY, locale="en-GB")

            assert reading.positions[0].symbol == symbol
            assert reading.positions[0].selection.position_id in entries


def test_en_us_tarot_falls_back_to_en_gb_dataset_without_changing_draw() -> None:
    engine = build_engine()
    american = ReadingRequest(
        spread_id=SINGLE_CARD.id,
        deck_id=RWS_DECK.id,
    )

    american_reading = engine.read(american, rng=SequenceRng(ints=range(78)))
    lookup = RWS_REGISTRY.lookup("en-US")
    entries = interpret(american_reading, RWS_REGISTRY, locale="en-US")

    assert lookup.data == RWS_EN_GB
    position_id = american_reading.positions[0].selection.position_id
    assert entries[position_id].source is not None
    assert "locale_fallback=en-US->en-GB" in lookup.provenance_notes


def test_unsupported_tarot_locale_keeps_draw_but_omits_interpretation() -> None:
    request = ReadingRequest(
        spread_id=SINGLE_CARD.id,
        deck_id=RWS_DECK.id,
    )

    reading = build_engine().read(request, rng=SequenceRng(ints=range(78)))
    lookup = RWS_REGISTRY.lookup("fr-FR")
    entries = interpret(reading, RWS_REGISTRY, locale="fr-FR")

    assert reading.draw.selections[0].symbol_id == RWS_DECK.symbols[0].id
    assert lookup.data is None
    assert entries == {}
    assert "resolved_locale=fr-FR" in lookup.provenance_notes
