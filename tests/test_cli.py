"""Smoke tests for the interpretation demo CLI."""

from __future__ import annotations

import json

import pytest

from fortune_telling_core._interpreter_cli import main

# Each tradition plus the inputs it needs (engine inputs have no defaults).
_BIRTH = ["--birth-datetime", "1990-01-01T12:00:00+00:00"]
_CHART = [*_BIRTH, "--latitude", "51.5", "--longitude", "-0.1"]
DEMO_ARGS: dict[str, list[str]] = {
    "tarot": ["--seed", "42"],
    "runes": ["--seed", "42"],
    "lenormand": ["--seed", "42"],
    "iching": ["--seed", "42"],
    "dominoes": ["--seed", "42"],
    "geomancy": ["--seed", "42"],
    "astrology": _CHART,
    "four-pillars": [*_CHART, "--gender", "male", "--target-year", "2026"],
    "nine-star-ki": [*_CHART, "--target-year", "2026"],
    "can-chi": _BIRTH,
    "celtic-tree": _BIRTH,
    "numerology": _BIRTH,
    "thaksa": _BIRTH,
    "tzolkin": _BIRTH,
    "weton": _BIRTH,
    "haab": _BIRTH,
    "koyomi": _BIRTH,
    "sanmeigaku": _BIRTH,
    "sukuyo": _BIRTH,
    "zi-wei": _BIRTH,
    "chaldean-numerology": ["--name", "Ada Lovelace"],
    "name-numerology": ["--name", "Ada Lovelace"],
    "cyrillic-pythagorean": ["--name", "Анна Иванова"],
    "cyrillic-slavonic-numerals": ["--name", "Анна"],
    "greek-isopsephy": ["--name", "Σωκράτης"],
    "cjk-name-strokes": ["--surname", "山田", "--given-name", "太郎"],
}


@pytest.mark.parametrize("demo", list(DEMO_ARGS))
def test_text_mode_runs_and_localizes(demo: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([demo, *DEMO_ARGS[demo], "--locale", "fr-FR", "--positions", "2"]) == 0
    out = capsys.readouterr().out
    assert "[fr-FR]" in out
    assert "Positions:" in out
    assert "skipped" not in out and "could not build reading" not in out


def test_as_of_adds_transits_to_astrology(capsys: pytest.CaptureFixture[str]) -> None:
    # --as-of layers transit-to-natal aspects onto the timeless natal chart.
    assert (
        main(["astrology", *_CHART, "--as-of", "2026-03-01T12:00:00+00:00", "--positions", "3"])
        == 0
    )
    out = capsys.readouterr().out
    assert "Summary:" in out
    assert "Transits as of 2026-03-01" in out
    # Aspects are now interpreted, not just summarized: natal + transit blocks.
    assert "Aspects:" in out
    assert "Transits:" in out
    assert "transit " in out and "natal " in out


def test_natal_astrology_interprets_aspects_without_transits(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Without --as-of the chart is timeless: natal aspects are interpreted, no transits.
    assert main(["astrology", *_CHART, "--positions", "3"]) == 0
    out = capsys.readouterr().out
    assert "Aspects:" in out
    assert "Transits:" not in out


def test_as_of_now_is_accepted(capsys: pytest.CaptureFixture[str]) -> None:
    # The literal "now" resolves to the current moment.
    assert main(["astrology", *_CHART, "--as-of", "now", "--positions", "0"]) == 0
    out = capsys.readouterr().out
    assert "Transits as of" in out


def test_four_pillars_target_year_is_optional(capsys: pytest.CaptureFixture[str]) -> None:
    # --target-year now overrides --as-of rather than being required; the annual
    # pillar still resolves from the reference time when it is omitted.
    assert main(["four-pillars", *_CHART, "--gender", "male", "--positions", "0"]) == 0
    out = capsys.readouterr().out
    assert "could not build reading" not in out and "skipped" not in out
    assert "Annual pillar" in out


def test_missing_input_for_named_tradition_is_a_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # No --seed for a drawn tradition: must not call the engine; reports and exits 2.
    assert main(["tarot"]) == 2
    out = capsys.readouterr().out
    assert "skipped: requires --seed" in out


def test_all_mode_skips_traditions_without_inputs(capsys: pytest.CaptureFixture[str]) -> None:
    # With only --seed, the drawn traditions build and the rest are skipped, exit 0.
    assert main(["--seed", "7", "--positions", "1"]) == 0
    out = capsys.readouterr().out
    assert "Tarot" in out and "Positions:" in out  # a drawn tradition built
    assert "skipped: requires --birth-datetime" in out  # a birth tradition skipped
    assert "skipped: requires --name" in out  # a name tradition skipped


def test_all_mode_routes_name_by_script(capsys: pytest.CaptureFixture[str]) -> None:
    # A Greek --name in 'all' mode reaches only the Greek tradition; others are skipped,
    # never invoked with an incompatible name.
    assert main(["--name", "Πλάτων", "--positions", "1"]) == 0
    out = capsys.readouterr().out
    assert "could not build reading" not in out


def test_single_tradition_honours_name_and_engine_validates(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # A single tradition gets the name as given; a bad script is a build failure (exit 1).
    assert main(["greek-isopsephy", "--name", "Bob"]) == 1
    assert "could not build reading" in capsys.readouterr().out


def test_list_traditions(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list-traditions"]) == 0
    out = capsys.readouterr().out
    assert "required inputs" in out
    assert "greek-isopsephy" in out and "name (Greek script)" in out
    assert "cjk-name-strokes" in out and "surname, given-name" in out


def test_list_locales(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list-locales"]) == 0
    locales = capsys.readouterr().out.split()
    assert {"en-GB", "en-US", "fr-FR", "ja-JP"} <= set(locales)


def test_json_mode_emits_reading_and_interpretation(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["tarot", "--seed", "42", "--json", "--locale", "ja-JP"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["tradition"] == "tarot"
    assert payload[0]["status"] == "ok"
    assert payload[0]["reading"]["spread"]
    assert payload[0]["interpretation"]


def test_deterministic_seed(capsys: pytest.CaptureFixture[str]) -> None:
    main(["tarot", "--seed", "7"])
    first = capsys.readouterr().out
    main(["tarot", "--seed", "7"])
    assert capsys.readouterr().out == first
