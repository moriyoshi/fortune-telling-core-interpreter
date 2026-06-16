"""CJK name-stroke (五格) luck stroke-count interpretation datasets across locales.

Each five-grid value resolves to a stroke count in 1-81, and that count carries a
luck rating. Schools disagree on both the tier count (binary 吉/凶, the Chinese
五格 three tiers 吉/半吉/凶, or the Kumazaki five tiers 大吉/吉/半吉/凶/大凶) and on
individual assignments, so the rating table is a **caller-selectable scheme**
rather than a single baked-in table.

Each scheme is a language-neutral number->rating map (here in code); the rating
words and per-count theme phrases come from JSON bundles under
``locales/stroke_count/<locale>.json``. Every scheme builds its own registry,
all keyed ``cjk_name_strokes.stroke_count.<n>`` so the caller composes the chosen
one with the per-grid axis dataset (:data:`CJK_NAME_STROKES_REGISTRY`);
``interpret`` then merges the grid's axis sentence with its stroke-count reading.

Schemes:

- ``"kumazaki"`` (default) - the Kumazaki 熊﨑式 five-tier table, the de-facto
  standard for Japanese seimei-handan. Source: kosazukari seimei-handan, citing
  熊崎健翁『姓名の神秘』(1929) and 五聖閣『完全マスター姓名判断』(2018).
- ``"chinese_wuge"`` - the Chinese 五格剖象法 three-tier table (吉/半吉/凶), a
  1936 re-import of the Kumazaki system. Source: meimingteng / 360doc 81数理表.

See :func:`fortune_telling_core.interpretation._stroke_count` for the lookup side.
"""

from __future__ import annotations

from collections.abc import Mapping

from fortune_telling_core.errors import ValidationError

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_ANCHOR = __name__.rpartition(".")[0]

# Kumazaki 熊﨑式 five-tier table (大吉/吉/半吉/凶/大凶), the de-facto seimei-handan
# standard. Transcribed from kosazukari's complete 81-count list.
_KUMAZAKI: dict[int, str] = {
    1: "great_fortune",
    2: "misfortune",
    3: "great_fortune",
    4: "misfortune",
    5: "great_fortune",
    6: "great_fortune",
    7: "fortune",
    8: "fortune",
    9: "misfortune",
    10: "misfortune",
    11: "great_fortune",
    12: "misfortune",
    13: "great_fortune",
    14: "misfortune",
    15: "great_fortune",
    16: "great_fortune",
    17: "fortune",
    18: "fortune",
    19: "misfortune",
    20: "misfortune",
    21: "great_fortune",
    22: "misfortune",
    23: "great_fortune",
    24: "great_fortune",
    25: "fortune",
    26: "misfortune",
    27: "misfortune",
    28: "misfortune",
    29: "fortune",
    30: "half_fortune",
    31: "great_fortune",
    32: "great_fortune",
    33: "great_fortune",
    34: "great_misfortune",
    35: "fortune",
    36: "misfortune",
    37: "great_fortune",
    38: "half_fortune",
    39: "fortune",
    40: "misfortune",
    41: "great_fortune",
    42: "misfortune",
    43: "misfortune",
    44: "great_misfortune",
    45: "great_fortune",
    46: "misfortune",
    47: "great_fortune",
    48: "great_fortune",
    49: "misfortune",
    50: "misfortune",
    51: "half_fortune",
    52: "fortune",
    53: "misfortune",
    54: "great_misfortune",
    55: "half_fortune",
    56: "misfortune",
    57: "fortune",
    58: "half_fortune",
    59: "misfortune",
    60: "misfortune",
    61: "great_fortune",
    62: "misfortune",
    63: "great_fortune",
    64: "great_misfortune",
    65: "great_fortune",
    66: "misfortune",
    67: "great_fortune",
    68: "great_fortune",
    69: "misfortune",
    70: "misfortune",
    71: "half_fortune",
    72: "misfortune",
    73: "half_fortune",
    74: "misfortune",
    75: "half_fortune",
    76: "misfortune",
    77: "half_fortune",
    78: "half_fortune",
    79: "misfortune",
    80: "misfortune",
    81: "great_fortune",
}

# Chinese 五格剖象法 three-tier table (吉/半吉/凶). A 1936 re-import of the Kumazaki
# system that flattens the two "great" tiers and reassigns several counts.
_CHINESE_WUGE: dict[int, str] = {
    **{
        n: "fortune"
        for n in (
            1,
            3,
            5,
            6,
            7,
            8,
            11,
            13,
            15,
            16,
            18,
            21,
            23,
            24,
            25,
            31,
            32,
            33,
            35,
            37,
            39,
            41,
            45,
            47,
            48,
            52,
            57,
            61,
            63,
            65,
            67,
            68,
            81,
        )
    },
    **{n: "half_fortune" for n in (17, 26, 27, 29, 30, 38, 49, 51, 55, 58, 71, 73, 75, 77, 78)},
    **{
        n: "misfortune"
        for n in (
            2,
            4,
            9,
            10,
            12,
            14,
            19,
            20,
            22,
            28,
            34,
            36,
            40,
            42,
            43,
            44,
            46,
            50,
            53,
            54,
            56,
            59,
            60,
            62,
            64,
            66,
            69,
            70,
            72,
            74,
            76,
            79,
            80,
        )
    },
}

# name -> (number->rating map, provenance string). The first entry is the default.
SCHEMES: dict[str, tuple[Mapping[int, str], str]] = {
    "kumazaki": (
        _KUMAZAKI,
        "fortune-telling-core cjk_name_strokes stroke-count, kumazaki five-tier v1",
    ),
    "chinese_wuge": (
        _CHINESE_WUGE,
        "fortune-telling-core cjk_name_strokes stroke-count, chinese wuge three-tier v1",
    ),
}

DEFAULT_SCHEME = "kumazaki"

for _name, (_ratings, _src) in SCHEMES.items():
    if set(_ratings) != set(range(1, 82)):  # pragma: no cover - guarded constants
        raise ValidationError(f"stroke-count scheme {_name!r} must not skip any count 1-81")


def _scheme_registry(
    scheme: str, ratings_map: Mapping[int, str], source: str
) -> InterpretationRegistry:
    def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
        reading = bundle.template("reading")
        ratings = bundle.group("ratings")
        themes = bundle.group("themes")
        entries: list[InterpretationEntry] = []
        for number in range(1, 82):
            rating_key = ratings_map[number]
            text = reading.format(
                number=number,
                rating=ratings[rating_key],
                theme=themes[str(number)],
            )
            entries.append(
                InterpretationEntry(
                    key=InterpretationKey(symbol_id=f"cjk_name_strokes.stroke_count.{number}"),
                    text=text,
                    keywords=(f"stroke-count-{number}", rating_key, scheme),
                    source=source,
                )
            )
        return MappingInterpretationData(
            id=f"cjk_name_strokes.stroke_count.{scheme}.{locale}.v1", entries=tuple(entries)
        )

    return InterpretationRegistry(build_all(_ANCHOR, "stroke_count", _build))


# One registry per rating scheme; the caller picks which to compose.
STROKE_COUNT_REGISTRIES: dict[str, InterpretationRegistry] = {
    name: _scheme_registry(name, ratings_map, source)
    for name, (ratings_map, source) in SCHEMES.items()
}

# Backwards-compatible default-scheme handles.
STROKE_COUNT_RATINGS: Mapping[int, str] = SCHEMES[DEFAULT_SCHEME][0]
CJK_NAME_STROKES_STROKE_COUNT_REGISTRY = STROKE_COUNT_REGISTRIES[DEFAULT_SCHEME]
CJK_NAME_STROKES_STROKE_COUNT_EN_GB = CJK_NAME_STROKES_STROKE_COUNT_REGISTRY.datasets["en-GB"]
CJK_NAME_STROKES_STROKE_COUNT_EN_US = CJK_NAME_STROKES_STROKE_COUNT_REGISTRY.datasets["en-US"]
CJK_NAME_STROKES_STROKE_COUNT_JA_JP = CJK_NAME_STROKES_STROKE_COUNT_REGISTRY.datasets["ja-JP"]

__all__ = [
    "CJK_NAME_STROKES_STROKE_COUNT_EN_GB",
    "CJK_NAME_STROKES_STROKE_COUNT_EN_US",
    "CJK_NAME_STROKES_STROKE_COUNT_JA_JP",
    "CJK_NAME_STROKES_STROKE_COUNT_REGISTRY",
    "DEFAULT_SCHEME",
    "SCHEMES",
    "STROKE_COUNT_RATINGS",
    "STROKE_COUNT_REGISTRIES",
]
