"""Nine Star Ki position interpretation datasets across locales.

Position text lives in JSON bundles under ``locales/positions/<locale>.json`` as
the ``texts`` vocab group (keyed by position id); there is no template.
"""

from __future__ import annotations

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = "fortune-telling-core Nine Star Ki reference data, positions v1"
_ANCHOR = __name__.rpartition(".")[0]


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    texts = bundle.group("texts")
    return MappingInterpretationData(
        id=f"nsk.positions.{locale}.v1",
        entries=tuple(
            InterpretationEntry(
                InterpretationKey("nsk.position", position_id=position_id),
                text,
                (position_id,),
                _SOURCE,
            )
            for position_id, text in texts.items()
        ),
    )


_DATASETS = build_all(_ANCHOR, "positions", _build)

POSITION_EN_GB = _DATASETS["en-GB"]
POSITION_EN_US = _DATASETS["en-US"]
POSITION_FR_FR = _DATASETS["fr-FR"]
POSITION_JA_JP = _DATASETS["ja-JP"]
POSITION_REGISTRY = InterpretationRegistry(_DATASETS)
