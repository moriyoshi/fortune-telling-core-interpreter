"""CJK name-stroke luck readings: stroke-count lookup and axis composition."""

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
from fortune_telling_core.traditions.cjk_name_strokes.interpretation import (
    CJK_NAME_STROKES_REGISTRY,
    CJK_NAME_STROKES_STROKE_COUNT_REGISTRY,
    DEFAULT_SCHEME,
    SCHEMES,
    STROKE_COUNT_REGISTRIES,
)
from fortune_telling_core.traditions.cjk_name_strokes.interpretation.stroke_count import (
    STROKE_COUNT_RATINGS,
)

_SOURCES = (CJK_NAME_STROKES_REGISTRY, CJK_NAME_STROKES_STROKE_COUNT_REGISTRY)


def _sources(scheme: str) -> tuple[object, object]:
    return (CJK_NAME_STROKES_REGISTRY, STROKE_COUNT_REGISTRIES[scheme])


def _grid_reading(value: str) -> Reading:
    """A one-position reading for the heaven grid carrying ``value`` strokes."""

    symbol = Symbol(
        "cjk_name_strokes.result.heaven",
        "Heaven Grid",
        attributes={"kind": "stroke_grid", "grid_position": "heaven"},
    )
    position = Position("heaven", "Heaven")
    selection = Selection("heaven", symbol.id, {"value": value})
    return Reading(
        request=ReadingRequest(deck_id="deck", spread_id="spread"),
        spread=Spread("spread", "Spread", (position,)),
        draw=Draw("deck", "spread", (selection,)),
        positions=(PositionReading(position, symbol, selection),),
        summary=None,
        provenance=Provenance("engine", "1", "core", "deck", "spread"),
        schema_version=1,
    )


def test_every_scheme_covers_one_to_eighty_one() -> None:
    for scheme, registry in STROKE_COUNT_REGISTRIES.items():
        data = registry.lookup("en-GB").data
        assert isinstance(data, MappingInterpretationData), scheme
        keys = {entry.key.symbol_id for entry in data.entries}
        assert keys == {f"cjk_name_strokes.stroke_count.{n}" for n in range(1, 82)}, scheme
    assert set(STROKE_COUNT_RATINGS) == set(range(1, 82))
    assert DEFAULT_SCHEME in SCHEMES


def test_axis_and_stroke_count_compose_into_one_reading() -> None:
    # Stroke count 11 is 大吉 (highly auspicious) in the Kumazaki table.
    entries = interpret(_grid_reading("11"), _SOURCES, locale="en-GB")
    text = entries["heaven"].text
    # The axis sentence is preserved...
    assert "Heaven Grid" in text
    # ...and the stroke-count luck reading is appended.
    assert "stroke count of 11" in text
    assert "highly auspicious" in text


def test_stroke_count_distinguishes_the_rating_tiers() -> None:
    # Kumazaki: 11=大吉, 8=吉, 30=半吉, 9=凶, 34=大凶.
    texts = {
        n: interpret(_grid_reading(str(n)), _SOURCES, locale="en-GB")["heaven"].text
        for n in (11, 8, 30, 9, 34)
    }
    assert "highly auspicious" in texts[11]
    assert "auspicious" in texts[8] and "highly auspicious" not in texts[8]
    assert "mixed" in texts[30]
    assert "inauspicious" in texts[9] and "highly inauspicious" not in texts[9]
    assert "highly inauspicious" in texts[34]


def test_scheme_selection_changes_the_rating() -> None:
    # Count 26 is 凶 (inauspicious) under Kumazaki but 半吉 (mixed) under the
    # Chinese 五格 scheme — selecting the scheme changes the reading.
    kumazaki = interpret(_grid_reading("26"), _sources("kumazaki"), locale="en-GB")["heaven"].text
    chinese = interpret(_grid_reading("26"), _sources("chinese_wuge"), locale="en-GB")[
        "heaven"
    ].text
    assert "inauspicious" in kumazaki
    assert "mixed" in chinese
    assert kumazaki != chinese


def test_stroke_count_above_eighty_one_wraps_into_range() -> None:
    # 82 wraps to 2 (subtract 80); both resolve to the same luck reading.
    wrapped = interpret(_grid_reading("82"), _SOURCES, locale="en-GB")["heaven"].text
    direct = interpret(_grid_reading("2"), _SOURCES, locale="en-GB")["heaven"].text
    assert "stroke count of 2" in wrapped
    assert wrapped == direct


def test_axis_only_when_value_missing() -> None:
    symbol = Symbol(
        "cjk_name_strokes.result.heaven",
        "Heaven Grid",
        attributes={"kind": "stroke_grid", "grid_position": "heaven"},
    )
    position = Position("heaven", "Heaven")
    selection = Selection("heaven", symbol.id, {})
    reading = Reading(
        request=ReadingRequest(deck_id="deck", spread_id="spread"),
        spread=Spread("spread", "Spread", (position,)),
        draw=Draw("deck", "spread", (selection,)),
        positions=(PositionReading(position, symbol, selection),),
        summary=None,
        provenance=Provenance("engine", "1", "core", "deck", "spread"),
        schema_version=1,
    )
    text = interpret(reading, _SOURCES, locale="en-GB")["heaven"].text
    assert "Heaven Grid" in text
    assert "stroke count" not in text
