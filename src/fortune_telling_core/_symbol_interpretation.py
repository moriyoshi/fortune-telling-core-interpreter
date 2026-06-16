"""Generic symbol-keyed interpretation datasets driven by locale bundles.

Most traditions need only a meaning per deck symbol. This builds such datasets
uniformly: structure (the symbol ids and their order) comes from a core deck,
while the per-symbol text comes from JSON locale bundles
(:mod:`fortune_telling_core._interpretation_bundle`). The bundle ``vocab`` is
keyed by the full symbol id.

- ``symbol_registry`` - one entry per symbol, from a ``meanings`` group.
- ``reversible_registry`` - upright (also the default, unmodified key) and
  reversed entries, from ``upright`` and ``reversed`` groups.
"""

from __future__ import annotations

from collections.abc import Sequence

from fortune_telling_core.symbols import Symbol

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)


def _keyword(symbol_id: str) -> str:
    return symbol_id.rsplit(".", 1)[-1]


def symbol_registry(
    anchor: str,
    dataset: str,
    dataset_id: str,
    symbols: Sequence[Symbol],
    source: str,
) -> InterpretationRegistry:
    """Registry of one-meaning-per-symbol datasets across all bundle locales."""

    def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
        meanings = bundle.group("meanings")
        return MappingInterpretationData(
            id=f"{dataset_id}.{locale}.v1",
            entries=tuple(
                InterpretationEntry(
                    InterpretationKey(symbol.id),
                    meanings[symbol.id],
                    (_keyword(symbol.id),),
                    source,
                )
                for symbol in symbols
            ),
        )

    return InterpretationRegistry(build_all(anchor, dataset, _build))


def reversible_registry(
    anchor: str,
    dataset: str,
    dataset_id: str,
    symbols: Sequence[Symbol],
    source: str,
) -> InterpretationRegistry:
    """Registry of upright/reversed datasets across all bundle locales."""

    def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
        upright = bundle.group("upright")
        reversed_text = bundle.group("reversed")
        entries: list[InterpretationEntry] = []
        for symbol in symbols:
            for variant in (None, "upright"):
                entries.append(
                    InterpretationEntry(
                        InterpretationKey(symbol.id, variant=variant),
                        upright[symbol.id],
                        (_keyword(symbol.id),),
                        source,
                    )
                )
            entries.append(
                InterpretationEntry(
                    InterpretationKey(symbol.id, variant="reversed"),
                    reversed_text[symbol.id],
                    (_keyword(symbol.id), "reversed"),
                    source,
                )
            )
        return MappingInterpretationData(id=f"{dataset_id}.{locale}.v1", entries=tuple(entries))

    return InterpretationRegistry(build_all(anchor, dataset, _build))
