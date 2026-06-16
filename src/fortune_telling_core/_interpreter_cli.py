"""Command-line demonstration of locale-aware interpretation.

This mirrors the core project's ``fortune-telling-demo`` but layers the
interpreter's job on top: it builds a structural reading with a core engine and
then resolves localized interpretation text for it with ``interpret()`` and the
tradition's interpretation registry. Use ``--locale`` to switch languages.

Engine inputs have **no defaults**: each tradition requires its own parameters
and the CLI never calls an engine without them (see ``--list-traditions``). They
fall into four groups:

- Drawn decks (tarot, runes, lenormand, iching, dominoes, geomancy): ``--seed``.
- Birth charts (astrology, four-pillars, nine-star-ki): ``--birth-datetime``,
  ``--latitude``, ``--longitude`` (four-pillars also ``--gender``).
- Birth date only (can-chi, celtic-tree, numerology, thaksa, tzolkin, weton,
  haab, koyomi, sanmeigaku, sukuyo, zi-wei): ``--birth-datetime``.
- Name based (chaldean-numerology, name-numerology, cyrillic-pythagorean,
  cyrillic-slavonic-numerals, greek-isopsephy): ``--name`` (in the tradition's
  script); cjk-name-strokes uses ``--surname`` and ``--given-name``.

``--as-of`` adds time-varying fortunes to the timed traditions (astrology
transits, four-pillars/sanmeigaku/zi-wei 流年 and 大運/大限, nine-star-ki annual
chart, koyomi almanac date); ``--target-year`` overrides it for the pillars.
``--locale`` and ``--positions`` are presentation options and keep defaults.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from fortune_telling_core.draw import Selection

from fortune_telling_core import Querent, RandomRng, Reading, ReadingRequest, Rng
from fortune_telling_core.interpretation import InterpretationEntry, interpret, interpret_extras
from fortune_telling_core.traditions import (
    astrology,
    can_chi,
    celtic_tree,
    chaldean_numerology,
    cjk_name_strokes,
    cyrillic_pythagorean,
    cyrillic_slavonic_numerals,
    dominoes,
    four_pillars,
    geomancy,
    greek_isopsephy,
    haab,
    iching,
    koyomi,
    lenormand,
    name_numerology,
    nine_star_ki,
    numerology,
    runes,
    sanmeigaku,
    sukuyo,
    tarot,
    thaksa,
    tzolkin,
    weton,
    zi_wei,
)
from fortune_telling_core.traditions.astrology.interpretation import (
    ASTRO_ASPECT_REGISTRY,
    ASTRO_HOUSE_REGISTRY,
    ASTRO_SIGN_REGISTRY,
)
from fortune_telling_core.traditions.can_chi.interpretation import CAN_CHI_REGISTRY
from fortune_telling_core.traditions.celtic_tree.interpretation import CELTIC_TREE_REGISTRY
from fortune_telling_core.traditions.chaldean_numerology.interpretation import (
    CHALDEAN_NUMEROLOGY_REGISTRY,
)
from fortune_telling_core.traditions.cjk_name_strokes.interpretation import (
    CJK_NAME_STROKES_REGISTRY,
    DEFAULT_SCHEME,
    SCHEMES,
    STROKE_COUNT_REGISTRIES,
)
from fortune_telling_core.traditions.cyrillic_pythagorean.interpretation import (
    CYRILLIC_PYTHAGOREAN_REGISTRY,
)
from fortune_telling_core.traditions.cyrillic_slavonic_numerals.interpretation import (
    CYRILLIC_SLAVONIC_NUMERALS_REGISTRY,
)
from fortune_telling_core.traditions.dominoes.interpretation import DOMINOES_REGISTRY
from fortune_telling_core.traditions.four_pillars.interpretation import (
    BRANCH_REGISTRY,
    STEM_REGISTRY,
    TEN_GODS_REGISTRY,
)
from fortune_telling_core.traditions.geomancy.interpretation import GEOMANCY_REGISTRY
from fortune_telling_core.traditions.greek_isopsephy.interpretation import GREEK_ISOPSEPHY_REGISTRY
from fortune_telling_core.traditions.haab.interpretation import HAAB_REGISTRY
from fortune_telling_core.traditions.iching.interpretation import ICHING_REGISTRY
from fortune_telling_core.traditions.koyomi.interpretation import KOYOMI_REGISTRY
from fortune_telling_core.traditions.lenormand.interpretation import LENORMAND_REGISTRY
from fortune_telling_core.traditions.name_numerology.interpretation import NAME_NUMEROLOGY_REGISTRY
from fortune_telling_core.traditions.nine_star_ki.interpretation import (
    POSITION_REGISTRY,
    STAR_REGISTRY,
)
from fortune_telling_core.traditions.numerology.interpretation import NUMEROLOGY_REGISTRY
from fortune_telling_core.traditions.runes.interpretation import RUNES_REGISTRY
from fortune_telling_core.traditions.sanmeigaku.interpretation import SANMEIGAKU_REGISTRY
from fortune_telling_core.traditions.sukuyo.interpretation import SUKUYO_REGISTRY
from fortune_telling_core.traditions.tarot.interpretation import RWS_REGISTRY
from fortune_telling_core.traditions.thaksa.interpretation import THAKSA_REGISTRY
from fortune_telling_core.traditions.tzolkin.interpretation import TZOLKIN_REGISTRY
from fortune_telling_core.traditions.weton.interpretation import WETON_REGISTRY
from fortune_telling_core.traditions.zi_wei.interpretation import ZI_WEI_PALACE_REGISTRY

_DEMO_REQUESTED_AT = datetime.fromisoformat("2026-01-01T12:00:00+00:00")
_DEFAULT_LOCALE = "en-GB"
_DEFAULT_POSITIONS = 6

# Any registry carries the full advertised locale set; used for --list-locales.
_REFERENCE_REGISTRY = RWS_REGISTRY

# Map each engine-input arg attribute to the flag a user passes, for messages.
_FLAG = {
    "seed": "--seed",
    "birth_datetime": "--birth-datetime",
    "latitude": "--latitude",
    "longitude": "--longitude",
    "gender": "--gender",
    "target_year": "--target-year",
    "name": "--name",
    "surname": "--surname",
    "given_name": "--given-name",
}


class _MissingInput(Exception):
    """Raised by a demo when the inputs it needs were not supplied."""


class _DrawEngine(Protocol):
    def read(self, request: ReadingRequest, *, rng: Rng) -> Reading: ...


class _CastEngine(Protocol):
    def cast(self, request: ReadingRequest) -> Reading: ...


@dataclass(frozen=True, slots=True)
class _Demo:
    key: str
    title: str
    # Human-readable summary of the inputs this tradition needs.
    inputs: str
    build: Callable[[argparse.Namespace], Reading]
    # One registry or a tuple of them, passed straight to interpret().
    source: object


@dataclass(frozen=True, slots=True)
class _Result:
    demo: _Demo
    reading: Reading | None
    entries: dict[str, InterpretationEntry]
    # Off-grid extras (e.g. astrology aspects): (selection, entry) in draw order.
    extras: list[tuple[Selection, InterpretationEntry | None]]
    # "ok" | "missing" | "error"; note carries the message for the latter two.
    kind: str
    note: str | None


def main(argv: Sequence[str] | None = None) -> int:
    """Run the interpretation demo CLI.

    Args:
        argv: Optional argument vector. When omitted, ``sys.argv`` is used.

    Returns:
        Process exit status.
    """

    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.list_locales:
        print(" ".join(sorted(_REFERENCE_REGISTRY.datasets)))
        return 0
    if args.list_traditions:
        print(_render_tradition_inputs())
        return 0

    results = _resolve(args)
    if args.json:
        print(json.dumps(_json_payload(results, args.locale), indent=2, ensure_ascii=False))
    else:
        print(_render(results, args.locale, args.positions))
    return _exit_code(args, results)


def _resolve(args: argparse.Namespace) -> list[_Result]:
    results: list[_Result] = []
    for demo in _selected_demos(args.demo):
        try:
            reading = demo.build(args)
        except _MissingInput as exc:
            results.append(_Result(demo, None, {}, [], "missing", str(exc)))
            continue
        except Exception as exc:  # an explicit but invalid input (e.g. wrong-script name)
            results.append(_Result(demo, None, {}, [], "error", f"{type(exc).__name__}: {exc}"))
            continue
        source = demo.source(args) if callable(demo.source) else demo.source
        entries = interpret(reading, source, locale=args.locale)
        extras = interpret_extras(reading, source, locale=args.locale)
        results.append(_Result(demo, reading, entries, extras, "ok", None))
    return results


def _exit_code(args: argparse.Namespace, results: list[_Result]) -> int:
    # In all-mode, missing-input traditions are simply skipped (exit 0). When a
    # single tradition is named, missing inputs are a usage error (2) and an
    # invalid input is a failure (1).
    if args.demo == "all":
        return 0
    if not results:
        return 0
    kind = results[0].kind
    if kind == "missing":
        return 2
    if kind == "error":
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fortune-telling-interpret",
        description=(
            "Build a reading with a core engine and resolve localized interpretation "
            "text for it. Engine inputs have no defaults; see --list-traditions."
        ),
    )
    parser.add_argument(
        "demo",
        nargs="?",
        default="all",
        choices=("all", *(_demo.key for _demo in _all_demos())),
        metavar="tradition",
        help="tradition to demonstrate (default: all); see --list-traditions",
    )
    parser.add_argument(
        "--locale",
        default=_DEFAULT_LOCALE,
        help="interpretation locale (e.g. en-GB, fr-FR, ja-JP); see --list-locales",
    )
    parser.add_argument(
        "--list-locales",
        action="store_true",
        help="list the available interpretation locales and exit",
    )
    parser.add_argument(
        "--list-traditions",
        action="store_true",
        help="list each tradition and the inputs it requires, then exit",
    )
    parser.add_argument("--json", action="store_true", help="emit reading + interpretation JSON")
    parser.add_argument("--seed", type=int, help="[drawn] RNG seed")
    parser.add_argument(
        "--positions",
        default=_DEFAULT_POSITIONS,
        type=int,
        help="maximum positions to show per reading in text mode",
    )
    parser.add_argument(
        "--birth-datetime",
        type=_parse_birth_datetime,
        help="[birth] birth datetime; naive values are read in the terminal timezone",
    )
    parser.add_argument(
        "--as-of",
        type=_parse_as_of,
        help=(
            "[timed] reference moment for time-varying fortunes (transits, 流年/大運, "
            "almanac date); 'now' or an ISO-8601 datetime, naive values use the terminal timezone"
        ),
    )
    parser.add_argument("--latitude", help="[birth chart] birth latitude")
    parser.add_argument("--longitude", help="[birth chart] birth longitude")
    parser.add_argument(
        "--gender",
        choices=("male", "female"),
        help="[four-pillars] luck-direction input; also enables 大運/大限 for sanmeigaku/zi-wei",
    )
    parser.add_argument(
        "--target-year",
        type=int,
        help="[four-pillars, nine-star-ki] annual year; overrides --as-of when given",
    )
    parser.add_argument(
        "--name",
        help=(
            "[name based] querent name, in the tradition's script (Latin/Cyrillic/Greek); "
            "in 'all' mode it is applied only to traditions whose script it matches"
        ),
    )
    parser.add_argument("--surname", help="[cjk-name-strokes] family name")
    parser.add_argument("--given-name", help="[cjk-name-strokes] given name")
    parser.add_argument(
        "--scheme",
        default=DEFAULT_SCHEME,
        choices=sorted(SCHEMES),
        help="[cjk-name-strokes] stroke-count luck rating scheme",
    )
    return parser


def _all_demos() -> tuple[_Demo, ...]:
    return (
        # Drawn decks: --seed.
        _Demo("tarot", "Tarot (Rider-Waite-Smith)", "seed (reversals)", _tarot, RWS_REGISTRY),
        _Demo("runes", "Elder Futhark runes", "seed (reversals)", _runes, RUNES_REGISTRY),
        _Demo("lenormand", "Petit Lenormand", "seed", _lenormand, LENORMAND_REGISTRY),
        _Demo("iching", "I Ching", "seed", _iching, ICHING_REGISTRY),
        _Demo("dominoes", "Dominoes", "seed", _dominoes, DOMINOES_REGISTRY),
        _Demo("geomancy", "Geomancy", "seed", _geomancy, GEOMANCY_REGISTRY),
        # Birth charts: birth datetime + location (+ gender / target year).
        _Demo(
            "astrology",
            "Astrology (natal)",
            "birth-datetime, latitude, longitude",
            _astrology,
            (ASTRO_SIGN_REGISTRY, ASTRO_HOUSE_REGISTRY, ASTRO_ASPECT_REGISTRY),
        ),
        _Demo(
            "four-pillars",
            "Four Pillars (BaZi)",
            "birth-datetime, latitude, longitude, gender, target-year",
            _four_pillars,
            (STEM_REGISTRY, BRANCH_REGISTRY, TEN_GODS_REGISTRY),
        ),
        _Demo(
            "nine-star-ki",
            "Nine Star Ki",
            "birth-datetime, latitude, longitude, target-year",
            _nine_star_ki,
            (STAR_REGISTRY, POSITION_REGISTRY),
        ),
        # Birth date only.
        _Demo("can-chi", "Can Chi", "birth-datetime", _can_chi, CAN_CHI_REGISTRY),
        _Demo("celtic-tree", "Celtic tree", "birth-datetime", _celtic_tree, CELTIC_TREE_REGISTRY),
        _Demo(
            "numerology", "Numerology (birth)", "birth-datetime", _numerology, NUMEROLOGY_REGISTRY
        ),
        _Demo("thaksa", "Thaksa", "birth-datetime", _thaksa, THAKSA_REGISTRY),
        _Demo("tzolkin", "Maya Tzolk'in", "birth-datetime", _tzolkin, TZOLKIN_REGISTRY),
        _Demo("weton", "Javanese weton", "birth-datetime", _weton, WETON_REGISTRY),
        _Demo("haab", "Maya Haab'", "birth-datetime", _haab, HAAB_REGISTRY),
        _Demo("koyomi", "Japanese koyomi (rokuyō)", "birth-datetime", _koyomi, KOYOMI_REGISTRY),
        _Demo(
            "sanmeigaku", "Sanmeigaku (算命学)", "birth-datetime", _sanmeigaku, SANMEIGAKU_REGISTRY
        ),
        _Demo("sukuyo", "Sukuyō (宿曜)", "birth-datetime", _sukuyo, SUKUYO_REGISTRY),
        _Demo(
            "zi-wei", "Zi Wei Dou Shu (紫微斗数)", "birth-datetime", _zi_wei, ZI_WEI_PALACE_REGISTRY
        ),
        # Name based.
        _Demo(
            "chaldean-numerology",
            "Chaldean numerology",
            "name (Latin script)",
            _chaldean,
            CHALDEAN_NUMEROLOGY_REGISTRY,
        ),
        _Demo(
            "name-numerology",
            "Name numerology",
            "name (Latin script)",
            _name_numerology,
            NAME_NUMEROLOGY_REGISTRY,
        ),
        _Demo(
            "cyrillic-pythagorean",
            "Cyrillic Pythagorean numerology",
            "name (Cyrillic script)",
            _cyrillic_pythagorean,
            CYRILLIC_PYTHAGOREAN_REGISTRY,
        ),
        _Demo(
            "cyrillic-slavonic-numerals",
            "Old Cyrillic numerals",
            "name (Cyrillic script)",
            _cyrillic_slavonic,
            CYRILLIC_SLAVONIC_NUMERALS_REGISTRY,
        ),
        _Demo(
            "greek-isopsephy",
            "Greek isopsephy",
            "name (Greek script)",
            _greek_isopsephy,
            GREEK_ISOPSEPHY_REGISTRY,
        ),
        _Demo(
            "cjk-name-strokes",
            "CJK name strokes",
            "surname, given-name (CJK)",
            _cjk_name_strokes,
            lambda args: (CJK_NAME_STROKES_REGISTRY, STROKE_COUNT_REGISTRIES[args.scheme]),
        ),
    )


def _selected_demos(name: str) -> tuple[_Demo, ...]:
    demos = _all_demos()
    if name == "all":
        return demos
    return tuple(demo for demo in demos if demo.key == name)


def _require(args: argparse.Namespace, *attrs: str) -> None:
    """Raise :class:`_MissingInput` listing any required inputs that are absent."""

    missing = [_FLAG[attr] for attr in attrs if getattr(args, attr) is None]
    if missing:
        raise _MissingInput("requires " + ", ".join(missing))


def _resolve_name(args: argparse.Namespace, script: str) -> str:
    if args.name is None:
        raise _MissingInput(f"requires --name (a {script}-script name)")
    # In all-mode a single --name only feeds the traditions whose script it
    # matches, so an engine never receives a name it cannot parse.
    if args.demo == "all" and _script_of(args.name) != script:
        raise _MissingInput(f"requires a {script}-script --name")
    name: str = args.name
    return name


def _drawn(deck_id: str, spread_id: str, engine: _DrawEngine, seed: int, **options: str) -> Reading:
    request = ReadingRequest(
        deck_id=deck_id, spread_id=spread_id, options=options, requested_at=_DEMO_REQUESTED_AT
    )
    return engine.read(request, rng=RandomRng(seed=seed))


def _cast(
    engine: _CastEngine,
    deck_id: str,
    spread_id: str,
    querent: Querent,
    *,
    as_of: datetime | None = None,
    **options: str,
) -> Reading:
    request = ReadingRequest(
        deck_id=deck_id,
        spread_id=spread_id,
        querent=querent,
        options=options,
        requested_at=_DEMO_REQUESTED_AT,
        as_of=as_of,
    )
    return engine.cast(request)


def _tarot(args: argparse.Namespace) -> Reading:
    _require(args, "seed")
    return _drawn(
        tarot.RWS_DECK.id,
        tarot.THREE_CARD.id,
        tarot.build_engine(),
        args.seed,
        allow_reversals="true",
    )


def _runes(args: argparse.Namespace) -> Reading:
    _require(args, "seed")
    return _drawn(
        runes.RUNE_DECK.id,
        runes.SINGLE_RUNE.id,
        runes.build_engine(),
        args.seed,
        allow_reversals="true",
    )


def _lenormand(args: argparse.Namespace) -> Reading:
    _require(args, "seed")
    return _drawn(
        lenormand.LENORMAND_DECK.id, lenormand.THREE_CARD.id, lenormand.build_engine(), args.seed
    )


def _iching(args: argparse.Namespace) -> Reading:
    _require(args, "seed")
    return _drawn(iching.ICHING_DECK.id, iching.CASTING.id, iching.build_engine(), args.seed)


def _dominoes(args: argparse.Namespace) -> Reading:
    _require(args, "seed")
    return _drawn(
        dominoes.DOMINOES_DECK.id, dominoes.THREE_TILES.id, dominoes.build_engine(), args.seed
    )


def _geomancy(args: argparse.Namespace) -> Reading:
    _require(args, "seed")
    return _drawn(geomancy.GEOMANCY_DECK.id, geomancy.SHIELD.id, geomancy.build_engine(), args.seed)


def _astrology(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime", "latitude", "longitude")
    # With --as-of, the natal chart gains transit-to-natal aspects for that moment.
    return _cast(
        astrology.build_engine(),
        astrology.TROPICAL_ZODIAC.id,
        astrology.NATAL_CHART.id,
        _birth_querent(args, latlon=True),
        as_of=args.as_of,
    )


def _four_pillars(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime", "latitude", "longitude", "gender")
    # The 流年 annual pillar follows --target-year when given, else --as-of, else now.
    options = {} if args.target_year is None else {"target_year": str(args.target_year)}
    return _cast(
        four_pillars.build_engine(),
        four_pillars.FOUR_PILLARS_DECK.id,
        four_pillars.FOUR_PILLARS_SPREAD.id,
        _birth_querent(args, latlon=True, gender=True),
        as_of=args.as_of,
        **options,
    )


def _nine_star_ki(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime", "latitude", "longitude")
    # The annual chart year follows --target-year when given, else --as-of, else now.
    options = {} if args.target_year is None else {"target_year": str(args.target_year)}
    return _cast(
        nine_star_ki.build_engine(),
        nine_star_ki.NINE_STAR_KI_DECK.id,
        nine_star_ki.NINE_STAR_KI_SPREAD.id,
        _birth_querent(args, latlon=True),
        as_of=args.as_of,
        **options,
    )


def _can_chi(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        can_chi.build_engine(),
        can_chi.CAN_CHI_DECK.id,
        can_chi.CAN_CHI_SPREAD.id,
        _birth_querent(args),
    )


def _celtic_tree(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        celtic_tree.build_engine(),
        celtic_tree.CELTIC_TREE_DECK.id,
        celtic_tree.CELTIC_TREE_SPREAD.id,
        _birth_querent(args),
    )


def _numerology(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        numerology.build_engine(),
        numerology.NUMEROLOGY_DECK.id,
        numerology.NUMEROLOGY_SPREAD.id,
        _birth_querent(args),
    )


def _thaksa(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        thaksa.build_engine(), thaksa.THAKSA_DECK.id, thaksa.THAKSA_SPREAD.id, _birth_querent(args)
    )


def _tzolkin(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        tzolkin.build_engine(),
        tzolkin.TZOLKIN_DECK.id,
        tzolkin.TZOLKIN_SPREAD.id,
        _birth_querent(args),
    )


def _weton(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        weton.build_engine(), weton.WETON_DECK.id, weton.WETON_SPREAD.id, _birth_querent(args)
    )


def _haab(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(haab.build_engine(), haab.HAAB_DECK.id, haab.HAAB_SPREAD.id, _birth_querent(args))


def _koyomi(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    # --as-of selects the almanac date; otherwise the birth date is used.
    return _cast(
        koyomi.build_engine(),
        koyomi.KOYOMI_DECK.id,
        koyomi.KOYOMI_SPREAD.id,
        _birth_querent(args),
        as_of=args.as_of,
    )


def _sanmeigaku(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    # --as-of adds 年運 annual stars (and 大運 luck cycles when --gender is given).
    return _cast(
        sanmeigaku.build_engine(),
        sanmeigaku.SANMEIGAKU_DECK.id,
        sanmeigaku.SANMEIGAKU_SPREAD.id,
        _birth_querent(args, gender=args.gender is not None),
        as_of=args.as_of,
    )


def _sukuyo(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    return _cast(
        sukuyo.build_engine(), sukuyo.SUKUYO_DECK.id, sukuyo.SUKUYO_SPREAD.id, _birth_querent(args)
    )


def _zi_wei(args: argparse.Namespace) -> Reading:
    _require(args, "birth_datetime")
    # --as-of adds the 流年 annual 命宮 (and the active 大限 decade with --gender).
    return _cast(
        zi_wei.build_engine(),
        zi_wei.ZI_WEI_DECK.id,
        zi_wei.ZI_WEI_SPREAD.id,
        _birth_querent(args, gender=args.gender is not None),
        as_of=args.as_of,
    )


def _chaldean(args: argparse.Namespace) -> Reading:
    return _cast(
        chaldean_numerology.build_engine(),
        chaldean_numerology.CHALDEAN_NUMEROLOGY_DECK.id,
        chaldean_numerology.CHALDEAN_NUMEROLOGY_SPREAD.id,
        _name_querent(_resolve_name(args, "latin")),
    )


def _name_numerology(args: argparse.Namespace) -> Reading:
    return _cast(
        name_numerology.build_engine(),
        name_numerology.NAME_NUMEROLOGY_DECK.id,
        name_numerology.NAME_NUMEROLOGY_SPREAD.id,
        _name_querent(_resolve_name(args, "latin")),
    )


def _cyrillic_pythagorean(args: argparse.Namespace) -> Reading:
    return _cast(
        cyrillic_pythagorean.build_engine(),
        cyrillic_pythagorean.CYRILLIC_PYTHAGOREAN_DECK.id,
        cyrillic_pythagorean.CYRILLIC_PYTHAGOREAN_SPREAD.id,
        _name_querent(_resolve_name(args, "cyrillic")),
    )


def _cyrillic_slavonic(args: argparse.Namespace) -> Reading:
    return _cast(
        cyrillic_slavonic_numerals.build_engine(),
        cyrillic_slavonic_numerals.CYRILLIC_SLAVONIC_NUMERALS_DECK.id,
        cyrillic_slavonic_numerals.CYRILLIC_SLAVONIC_NUMERALS_SPREAD.id,
        _name_querent(_resolve_name(args, "cyrillic")),
    )


def _greek_isopsephy(args: argparse.Namespace) -> Reading:
    return _cast(
        greek_isopsephy.build_engine(),
        greek_isopsephy.GREEK_ISOPSEPHY_DECK.id,
        greek_isopsephy.GREEK_ISOPSEPHY_SPREAD.id,
        _name_querent(_resolve_name(args, "greek")),
    )


def _cjk_name_strokes(args: argparse.Namespace) -> Reading:
    _require(args, "surname", "given_name")
    querent = Querent(
        id="demo",
        display_name="Demo Querent",
        attributes={"surname": args.surname, "given_name": args.given_name},
    )
    # Stroke counts default to core's bundled Unihan table; no explicit counts needed.
    return _cast(
        cjk_name_strokes.build_engine(),
        cjk_name_strokes.CJK_NAME_STROKES_DECK.id,
        cjk_name_strokes.CJK_NAME_STROKES_SPREAD.id,
        querent,
    )


def _birth_querent(
    args: argparse.Namespace, *, latlon: bool = False, gender: bool = False
) -> Querent:
    attributes = {"birth_datetime": str(args.birth_datetime)}
    if latlon:
        attributes["latitude"] = str(args.latitude)
        attributes["longitude"] = str(args.longitude)
    if gender:
        attributes["gender"] = args.gender
    return Querent(id="demo", display_name="Demo Querent", attributes=attributes)


def _name_querent(name: str) -> Querent:
    return Querent(id="demo", display_name="Demo Querent", attributes={"name": name})


def _script_of(text: str) -> str:
    """Classify a name by the first script letter it contains."""

    for char in text:
        code = ord(char)
        if 0x0370 <= code <= 0x03FF or 0x1F00 <= code <= 0x1FFF:
            return "greek"
        if 0x0400 <= code <= 0x04FF:
            return "cyrillic"
        if (char.isascii() and char.isalpha()) or 0x00C0 <= code <= 0x024F:
            return "latin"
    return "other"


def _parse_birth_datetime(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("birth datetime must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.astimezone()
    return parsed.isoformat()


def _parse_as_of(value: str) -> datetime:
    if value.strip().lower() == "now":
        return datetime.now().astimezone()
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("as-of must be 'now' or an ISO-8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.astimezone()
    return parsed


def _render_tradition_inputs() -> str:
    width = max(len(demo.key) for demo in _all_demos())
    lines = ["tradition".ljust(width) + "  required inputs"]
    for demo in _all_demos():
        lines.append(f"{demo.key.ljust(width)}  {demo.inputs}")
    return "\n".join(lines)


def _json_payload(results: list[_Result], locale: str) -> list[dict[str, object]]:
    payload: list[dict[str, object]] = []
    for result in results:
        item: dict[str, object] = {
            "tradition": result.demo.key,
            "locale": locale,
            "status": result.kind,
        }
        if result.reading is None:
            item["note"] = result.note
        else:
            item["reading"] = result.reading.to_dict()
            item["interpretation"] = {
                position_id: entry.to_dict() for position_id, entry in result.entries.items()
            }
            if result.extras:
                item["extras"] = [
                    {
                        "selection": selection.to_dict(),
                        "interpretation": entry.to_dict() if entry is not None else None,
                    }
                    for selection, entry in result.extras
                ]
        payload.append(item)
    return payload


def _render(results: list[_Result], locale: str, max_positions: int) -> str:
    return "\n\n".join(_render_one(result, locale, max_positions) for result in results)


def _render_one(result: _Result, locale: str, max_positions: int) -> str:
    demo = result.demo
    if result.reading is None:
        label = "skipped" if result.kind == "missing" else "could not build reading"
        return f"{demo.title}  [{locale}]\n  ({label}: {result.note})"
    reading = result.reading
    lines = [
        f"{demo.title}  [{locale}]",
        f"Spread: {reading.spread.name} ({reading.spread.id})",
    ]
    if reading.summary:
        lines.append(f"Summary: {reading.summary}")
    lines.append("Positions:")
    shown = reading.positions[: max(max_positions, 0)]
    for position in shown:
        entry = result.entries.get(position.selection.position_id)
        meaning = entry.text if entry is not None else "(no interpretation for this locale)"
        lines.append(f"- {position.position.name}: {position.symbol.name}")
        lines.append(f"    {meaning}")
    if len(reading.positions) > len(shown):
        lines.append(f"- ... {len(reading.positions) - len(shown)} more positions")
    _render_extras(lines, result.extras, max_positions)
    return "\n".join(lines)


# Off-grid extras grouped by their ``kind`` modifier, with a heading each.
_EXTRA_GROUPS: tuple[tuple[str, str], ...] = (("natal", "Aspects"), ("transit", "Transits"))


def _render_extras(
    lines: list[str],
    extras: list[tuple[Selection, InterpretationEntry | None]],
    max_positions: int,
) -> None:
    for kind, heading in _EXTRA_GROUPS:
        group = [(sel, entry) for sel, entry in extras if (sel.modifiers or {}).get("kind") == kind]
        if not group:
            continue
        lines.append(f"{heading}:")
        shown = group[: max(max_positions, 0)]
        for selection, entry in shown:
            meaning = entry.text if entry is not None else "(no interpretation for this locale)"
            lines.append(f"- {_aspect_label(selection, kind)}")
            lines.append(f"    {meaning}")
        if len(group) > len(shown):
            lines.append(f"- ... {len(group) - len(shown)} more")


def _aspect_label(selection: Selection, kind: str) -> str:
    modifiers = selection.modifiers or {}
    aspect = selection.symbol_id.rsplit(".", 1)[-1]
    first = _prettify(modifiers.get("first", "?"))
    second = _prettify(modifiers.get("second", "?"))
    orb = modifiers.get("orb")
    suffix = f" (orb {orb}°)" if orb else ""
    if kind == "transit":
        return f"transit {first} {aspect} natal {second}{suffix}"
    return f"{first} {aspect} {second}{suffix}"


def _prettify(token: str) -> str:
    return token.replace("_", " ").title()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
