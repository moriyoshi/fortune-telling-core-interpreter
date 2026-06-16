"""Astrology aspect interpretation datasets across locales.

Core emits each chart aspect (natal, and transit-to-natal when the request
carries ``as_of``) as a structured ``draw.extras`` selection keyed
``astro.aspect.<type>`` with ``{first, second, orb, kind}`` modifiers. This maps
the five Ptolemaic aspect types to localized meaning text; the participating
bodies and the natal/transit framing are composed by the caller (the CLI groups
``kind`` natal vs transit). Resolved via :func:`interpret_extras`. Translatable
text lives in JSON bundles under ``locales/aspects/<locale>.json``.
"""

from __future__ import annotations

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core astrology reference data, aspects v1"
_ANCHOR = __name__.rpartition(".")[0]

# The five Ptolemaic aspects, in the order core's DEFAULT_ASPECTS declares them.
_ASPECTS: tuple[str, ...] = ("conjunction", "opposition", "trine", "square", "sextile")


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    meanings = bundle.group("meanings")
    return MappingInterpretationData(
        id=f"astro.aspects.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey(symbol_id=f"astro.aspect.{aspect}"),
                meanings[aspect],
                (aspect,),
                _SOURCE,
            )
            for aspect in _ASPECTS
        ),
    )


_DATASETS = build_all(_ANCHOR, "aspects", _build)

ASTRO_ASPECT_EN_GB = _DATASETS["en-GB"]
ASTRO_ASPECT_EN_US = _DATASETS["en-US"]
ASTRO_ASPECT_REGISTRY = InterpretationRegistry(_DATASETS)
