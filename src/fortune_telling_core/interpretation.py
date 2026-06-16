"""Interpretation data contracts and mapping-backed implementation.

This is the package's public anchor module; it also exposes the distribution
version as ``__version__`` (the ``fortune_telling_core`` package root belongs to
the sibling ``fortune-telling-core`` package, so this layer cannot own it there).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, cast

from fortune_telling_core.coerce import (
    json_object,
    json_object_sequence,
    optional_str,
    require_str,
    str_sequence,
)
from fortune_telling_core.draw import Selection
from fortune_telling_core.errors import ValidationError
from fortune_telling_core.reading import PositionReading, Reading
from fortune_telling_core.serde_types import JsonMapping, JsonObject

try:
    # Single source of truth: _interpreter_version.py is generated from the git
    # tag by hatch-vcs at build/install time (see pyproject [tool.hatch.build.hooks.vcs]).
    from fortune_telling_core._interpreter_version import __version__
except ImportError:  # pragma: no cover - generated file absent in an unbuilt tree
    __version__ = "0.0.0+unknown"


@dataclass(frozen=True, slots=True)
class InterpretationKey:
    """Lookup key for interpretation text.

    Args:
        symbol_id: Symbol identifier to interpret.
        position_id: Optional spread position identifier.
        variant: Optional engine-specific variant such as `reversed` or
            `retrograde`.

    Raises:
        ValidationError: If `symbol_id` is empty or optional fields are empty
            strings.
    """

    symbol_id: str
    position_id: str | None = None
    variant: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol_id:
            raise ValidationError("interpretation key symbol_id must not be empty")
        if self.position_id == "":
            raise ValidationError("interpretation key position_id must not be empty")
        if self.variant == "":
            raise ValidationError("interpretation key variant must not be empty")

    def to_dict(self) -> JsonObject:
        """Serialize the key to a JSON-compatible dictionary."""

        result: JsonObject = {"symbol_id": self.symbol_id}
        if self.position_id is not None:
            result["position_id"] = self.position_id
        if self.variant is not None:
            result["variant"] = self.variant
        return result

    @classmethod
    def from_dict(cls, data: JsonMapping) -> InterpretationKey:
        """Deserialize an interpretation key.

        Args:
            data: JSON-compatible key mapping.

        Returns:
            The decoded key.

        Raises:
            ValidationError: If required fields are missing or malformed.
        """

        return cls(
            symbol_id=require_str(data, "symbol_id"),
            position_id=optional_str(data, "position_id"),
            variant=optional_str(data, "variant"),
        )


@dataclass(frozen=True, slots=True)
class InterpretationEntry:
    """Textual interpretation for one lookup key.

    Args:
        key: Lookup key this entry answers.
        text: Interpretation text.
        keywords: Search or summary keywords.
        source: Optional citation or dataset source.

    Raises:
        ValidationError: If `text` is empty.
    """

    key: InterpretationKey
    text: str
    keywords: Sequence[str] = ()
    source: str | None = None

    def __post_init__(self) -> None:
        if not self.text:
            raise ValidationError("interpretation text must not be empty")
        object.__setattr__(self, "keywords", tuple(self.keywords))

    def to_dict(self) -> JsonObject:
        """Serialize the entry to a JSON-compatible dictionary."""

        result: JsonObject = {
            "key": self.key.to_dict(),
            "text": self.text,
            "keywords": list(self.keywords),
        }
        if self.source is not None:
            result["source"] = self.source
        return result

    @classmethod
    def from_dict(cls, data: JsonMapping) -> InterpretationEntry:
        """Deserialize an interpretation entry.

        Args:
            data: JSON-compatible entry mapping.

        Returns:
            The decoded entry.

        Raises:
            ValidationError: If required fields are missing or malformed.
        """

        return cls(
            key=InterpretationKey.from_dict(json_object(data.get("key"), "key")),
            text=require_str(data, "text"),
            keywords=str_sequence(data.get("keywords", []), "keywords"),
            source=optional_str(data, "source"),
        )


class InterpretationData(Protocol):
    """Protocol for interpretation lookup datasets."""

    @property
    def id(self) -> str:
        """Stable identifier for this interpretation dataset."""

    def lookup(self, key: InterpretationKey) -> InterpretationEntry | None:
        """Return the best matching interpretation entry for `key`.

        Args:
            key: Desired symbol, position, and variant combination.

        Returns:
            A matching entry, or `None` if the dataset has no usable fallback.
        """


class LocaleDatasetLookup(Protocol):
    """Locale-aware dataset lookup result."""

    data: InterpretationData | None
    requested_locale: str
    normalized_locale: str
    resolved_locale: str


class LocaleInterpretationRegistry(Protocol):
    """Registry protocol implemented by ``InterpretationRegistry``."""

    datasets: Mapping[str, InterpretationData]

    def lookup(self, locale: str) -> LocaleDatasetLookup:
        """Return the best dataset for a requested locale."""


@dataclass(frozen=True, slots=True)
class MappingInterpretationData:
    """Mapping-backed interpretation dataset with fallback lookup.

    Lookup order is exact key, symbol plus variant, symbol plus position, then
    symbol only.

    Args:
        id: Stable dataset identifier.
        entries: Interpretation entries in the dataset.

    Raises:
        ValidationError: If the id is empty or keys are duplicated.
    """

    id: str
    entries: Sequence[InterpretationEntry]
    _index: Mapping[InterpretationKey, InterpretationEntry] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not self.id:
            raise ValidationError("interpretation data id must not be empty")
        entries = tuple(self.entries)
        index: dict[InterpretationKey, InterpretationEntry] = {}
        for entry in entries:
            if entry.key in index:
                raise ValidationError("interpretation keys must be unique")
            index[entry.key] = entry
        object.__setattr__(self, "entries", entries)
        object.__setattr__(self, "_index", index)

    def lookup(self, key: InterpretationKey) -> InterpretationEntry | None:
        """Look up an interpretation with graceful fallbacks.

        Args:
            key: Desired symbol, position, and variant combination.

        Returns:
            The first matching entry in the fallback chain, or `None`.
        """

        candidates = (
            key,
            InterpretationKey(key.symbol_id, None, key.variant),
            InterpretationKey(key.symbol_id, key.position_id, None),
            InterpretationKey(key.symbol_id, None, None),
        )
        for candidate in candidates:
            entry = self._index.get(candidate)
            if entry is not None:
                return entry
        return None

    def to_dict(self) -> JsonObject:
        """Serialize the dataset to a JSON-compatible dictionary."""

        return {
            "id": self.id,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: JsonMapping) -> MappingInterpretationData:
        """Deserialize a mapping-backed interpretation dataset.

        Args:
            data: JSON-compatible dataset mapping.

        Returns:
            The decoded dataset.

        Raises:
            ValidationError: If required fields are missing or malformed.
        """

        return cls(
            id=require_str(data, "id"),
            entries=tuple(
                InterpretationEntry.from_dict(item)
                for item in json_object_sequence(data.get("entries"), "entries")
            ),
        )


def interpret(
    reading: Reading,
    dataset_or_registry: object | Sequence[object],
    *,
    locale: str = "en-GB",
) -> dict[str, InterpretationEntry]:
    """Resolve interpretation entries for a structural core reading.

    Args:
        reading: Core reading produced by a structural engine.
        dataset_or_registry: One dataset, one locale-aware registry, or a
            sequence of datasets/registries to compose.
        locale: Requested locale when a registry is supplied.

    Returns:
        Mapping from spread position id to resolved interpretation entry.
    """

    datasets = tuple(_resolve_datasets(dataset_or_registry, locale))
    resolved: dict[str, InterpretationEntry] = {}
    for position in reading.positions:
        entry = _resolve_position(position, datasets)
        if entry is not None:
            resolved[position.selection.position_id] = entry
    return resolved


def interpret_extras(
    reading: Reading,
    dataset_or_registry: object | Sequence[object],
    *,
    locale: str = "en-GB",
) -> list[tuple[Selection, InterpretationEntry | None]]:
    """Resolve interpretation entries for a reading's off-grid extras.

    A reading's ``draw.extras`` holds structured selections not bound to a spread
    position (e.g. astrology aspects, keyed ``astro.aspect.<type>``), so they fall
    outside :func:`interpret`. This resolves each by its ``symbol_id`` (a
    ``kind`` modifier, when present, is tried as a variant first).

    Args:
        reading: Core reading produced by a structural engine.
        dataset_or_registry: One dataset, one locale-aware registry, or a
            sequence of datasets/registries to compose.
        locale: Requested locale when a registry is supplied.

    Returns:
        A list of ``(selection, entry)`` in draw order; ``entry`` is ``None``
        when no dataset covers the selection's symbol.
    """

    datasets = tuple(_resolve_datasets(dataset_or_registry, locale))
    extras = getattr(reading.draw, "extras", ()) or ()
    return [(selection, _resolve_selection(selection, datasets)) for selection in extras]


def _resolve_selection(
    selection: Selection,
    datasets: Sequence[InterpretationData],
) -> InterpretationEntry | None:
    modifiers = selection.modifiers or {}
    kind = modifiers.get("kind") or None
    keys = (
        InterpretationKey(symbol_id=selection.symbol_id, variant=kind),
        InterpretationKey(symbol_id=selection.symbol_id),
    )
    merged: InterpretationEntry | None = None
    for dataset in datasets:
        merged = _merge_entries(merged, _lookup_first(dataset, keys))
    return merged


def _resolve_datasets(
    source: object | Sequence[object],
    locale: str,
) -> tuple[InterpretationData, ...]:
    if isinstance(source, Sequence) and not hasattr(source, "lookup"):
        datasets: list[InterpretationData] = []
        for item in source:
            datasets.extend(_resolve_datasets(item, locale))
        return tuple(datasets)
    if hasattr(source, "datasets"):
        registry = cast(LocaleInterpretationRegistry, source)
        data = registry.lookup(locale).data
        return () if data is None else (data,)
    return (cast(InterpretationData, source),)


def _resolve_position(
    position: PositionReading,
    datasets: Sequence[InterpretationData],
) -> InterpretationEntry | None:
    merged: InterpretationEntry | None = None
    for dataset in datasets:
        entry = _lookup_first(dataset, _candidate_keys(position))
        merged = _merge_entries(merged, entry)
    return merged


def _lookup_first(
    dataset: InterpretationData,
    keys: Sequence[InterpretationKey],
) -> InterpretationEntry | None:
    for key in keys:
        entry = dataset.lookup(key)
        if entry is not None:
            return entry
    return None


def _candidate_keys(position: PositionReading) -> tuple[InterpretationKey, ...]:
    selection = position.selection
    modifiers = selection.modifiers or {}
    variant = _variant_from_modifiers(modifiers)
    keys = [
        InterpretationKey(
            symbol_id=position.symbol.id,
            position_id=selection.position_id,
            variant=variant,
        )
    ]
    house = modifiers.get("house")
    if house is not None:
        keys.append(InterpretationKey(f"astro.house.{house}", position_id=selection.position_id))
    stroke_count = _stroke_count(position.symbol, modifiers)
    if stroke_count is not None:
        keys.append(
            InterpretationKey(
                f"cjk_name_strokes.stroke_count.{stroke_count}",
                position_id=selection.position_id,
            )
        )
    if position.symbol.id.startswith("zi_wei."):
        # Zi Wei readings are interpreted per palace (the spread position), not by
        # the branch the palace lands on.
        keys.append(InterpretationKey("zi_wei.palace", position_id=selection.position_id))
    keys.append(InterpretationKey("nsk.position", position_id=selection.position_id))
    return tuple(keys)


def _stroke_count(symbol: object, modifiers: Mapping[str, str]) -> int | None:
    """Return the 1-81 stroke-grid count for a CJK name-stroke selection.

    The grid's raw stroke count rides on the ``value`` modifier; values above 81
    wrap back into the canonical 1-81 cycle (subtract 80 until in range), as the
    luck table only spans those numbers.
    """

    attributes = getattr(symbol, "attributes", None)
    if not attributes or attributes.get("kind") != "stroke_grid":
        return None
    value = modifiers.get("value")
    if value is None or not value.isdigit():
        return None
    number = int(value)
    if number < 1:
        return None
    while number > 81:
        number -= 80
    return number


def _variant_from_modifiers(modifiers: Mapping[str, str]) -> str | None:
    orientation = modifiers.get("orientation")
    if orientation is not None:
        return orientation
    if modifiers.get("retrograde") == "true":
        return "retrograde"
    ten_god = modifiers.get("ten_god")
    if modifiers.get("kind") == "stem" and ten_god not in {None, "day_master"}:
        return ten_god
    return modifiers.get("element")


def _merge_entries(
    first: InterpretationEntry | None,
    second: InterpretationEntry | None,
) -> InterpretationEntry | None:
    if first is None:
        return second
    if second is None:
        return first
    return InterpretationEntry(
        first.key,
        f"{first.text} {second.text}",
        tuple(dict.fromkeys((*first.keywords, *second.keywords))),
        _join_unique((first.source, second.source)),
    )


def _join_unique(values: Sequence[str | None]) -> str | None:
    unique = tuple(dict.fromkeys(value for value in values if value))
    if not unique:
        return None
    return "; ".join(unique)
