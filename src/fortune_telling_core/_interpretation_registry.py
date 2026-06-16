"""Locale-aware interpretation dataset lookup."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fortune_telling_core._locale import resolve_locale
from fortune_telling_core.interpretation import InterpretationData


@dataclass(frozen=True, slots=True)
class InterpretationDatasetLookup:
    """Result of a locale-aware interpretation dataset lookup."""

    data: InterpretationData | None
    requested_locale: str
    normalized_locale: str
    resolved_locale: str

    @property
    def provenance_notes(self) -> tuple[str, ...]:
        """Return audit notes for the lookup."""

        notes = [
            f"requested_locale={self.requested_locale}",
            f"resolved_locale={self.resolved_locale}",
        ]
        if self.resolved_locale != self.normalized_locale:
            notes.append(f"locale_fallback={self.normalized_locale}->{self.resolved_locale}")
        return tuple(notes)


@dataclass(frozen=True, slots=True)
class InterpretationRegistry:
    """Locale-indexed interpretation datasets for one dataset family."""

    datasets: Mapping[str, InterpretationData]

    def lookup(self, locale: str) -> InterpretationDatasetLookup:
        """Return the best dataset for a requested locale."""

        resolution = resolve_locale(locale)
        for candidate in resolution.candidates:
            data = self.datasets.get(candidate)
            if data is not None:
                return InterpretationDatasetLookup(
                    data=data,
                    requested_locale=resolution.requested,
                    normalized_locale=resolution.normalized,
                    resolved_locale=candidate,
                )
        return InterpretationDatasetLookup(
            data=None,
            requested_locale=resolution.requested,
            normalized_locale=resolution.normalized,
            resolved_locale=resolution.normalized,
        )
