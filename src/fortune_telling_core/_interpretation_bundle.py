"""Locale translation bundles: schema, loader, and en-US derivation.

Interpretation **text** is data, not code. Each dataset family ships one JSON
bundle per locale under ``<family package>/locales/<dataset>/<locale>.json`` with
this shape::

    {
        "schema_version": 1,
        "locale": "fr-FR",
        "templates": { "<name>": "<format string>", ... },
        "vocab":     { "<group>": { "<key>": "<translated string>", ... }, ... }
    }

The dataset builders stay in code and keep deriving structure (lookup keys,
keyword tokens, the set and order of signs/stems/cards) from ``fortune-telling-core``.
A bundle only supplies the translatable ``templates`` and ``vocab`` strings; the
builder joins them with the structural data. ``templates`` and ``vocab`` are both
optional and may be empty (prose datasets keep all their text in ``vocab``).

en-GB, fr-FR, and ja-JP are authored bundles. en-US is *derived* in code from the
en-GB bundle by :func:`americanize` (a British -> American spelling normalization),
so it never drifts from en-GB.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib.resources import files

from fortune_telling_core.errors import ValidationError

SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class LocaleBundle:
    """Parsed, validated translation bundle for one dataset and locale."""

    locale: str
    templates: Mapping[str, str]
    vocab: Mapping[str, Mapping[str, str]]

    def template(self, name: str) -> str:
        """Return a named format string, or raise if the bundle omits it."""

        try:
            return self.templates[name]
        except KeyError:
            raise ValidationError(f"bundle {self.locale!r} is missing template {name!r}") from None

    def group(self, name: str) -> Mapping[str, str]:
        """Return a named vocabulary group, or raise if the bundle omits it."""

        try:
            return self.vocab[name]
        except KeyError:
            raise ValidationError(
                f"bundle {self.locale!r} is missing vocab group {name!r}"
            ) from None


def load_bundle(anchor: str, dataset: str, locale: str) -> LocaleBundle:
    """Load and validate a locale bundle shipped as package data.

    Args:
        anchor: Import path of the package that owns the ``locales`` directory,
            normally the calling module's ``__package__``.
        dataset: Dataset family folder under ``locales`` (e.g. ``"signs"``).
        locale: Locale tag and file stem (e.g. ``"fr-FR"``).

    Returns:
        The parsed bundle.

    Raises:
        ValidationError: If the bundle is missing or malformed.
    """

    resource = files(anchor).joinpath("locales", dataset, f"{locale}.json")
    try:
        raw = json.loads(resource.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValidationError(
            f"no interpretation bundle for dataset {dataset!r} locale {locale!r}"
        ) from None
    return _parse(raw, dataset, locale)


def _parse(raw: object, dataset: str, locale: str) -> LocaleBundle:
    where = f"{dataset}/{locale}"
    if not isinstance(raw, dict):
        raise ValidationError(f"bundle {where} must be a JSON object")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValidationError(
            f"bundle {where} schema_version {raw.get('schema_version')!r} != {SCHEMA_VERSION}"
        )
    if raw.get("locale") != locale:
        raise ValidationError(
            f"bundle {where} declares locale {raw.get('locale')!r}, expected {locale!r}"
        )
    templates = _str_map(raw.get("templates", {}), f"{where} templates")
    vocab_raw = raw.get("vocab", {})
    if not isinstance(vocab_raw, dict):
        raise ValidationError(f"bundle {where} vocab must be a JSON object")
    vocab = {
        group: _str_map(values, f"{where} vocab.{group}") for group, values in vocab_raw.items()
    }
    return LocaleBundle(locale=locale, templates=templates, vocab=vocab)


def _str_map(value: object, where: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValidationError(f"{where} must be a JSON object")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ValidationError(f"{where} must map strings to strings")
        result[key] = item
    return result


# British -> American spellings present anywhere in the en-GB bundles. en-US is
# derived from en-GB at import time so the two never drift.
_BRITISH_TO_AMERICAN = {
    "stabilise": "stabilize",
    "internalised": "internalized",
    "judgement": "judgment",
    "fulfilment": "fulfillment",
    "prioritisation": "prioritization",
    "labour": "labor",
    "favoured": "favored",
    "pretence": "pretense",
    "emphasise": "emphasize",
    "emphasises": "emphasizes",
}
_AMERICAN_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(word) for word in _BRITISH_TO_AMERICAN) + r")\b"
)


def americanize(bundle: LocaleBundle) -> LocaleBundle:
    """Return an ``en-US`` bundle from an ``en-GB`` one via spelling normalization."""

    def fix(text: str) -> str:
        return _AMERICAN_PATTERN.sub(lambda m: _BRITISH_TO_AMERICAN[m.group(0)], text)

    return LocaleBundle(
        locale="en-US",
        templates={name: fix(value) for name, value in bundle.templates.items()},
        vocab={
            group: {key: fix(value) for key, value in items.items()}
            for group, items in bundle.vocab.items()
        },
    )


def available_locales(anchor: str, dataset: str) -> tuple[str, ...]:
    """Return the sorted locale tags that have a bundle file for ``dataset``."""

    directory = files(anchor).joinpath("locales", dataset)
    return tuple(
        sorted(
            item.name.removesuffix(".json")
            for item in directory.iterdir()
            if item.name.endswith(".json")
        )
    )


def build_all[T](
    anchor: str,
    dataset: str,
    builder: Callable[[str, LocaleBundle], T],
) -> dict[str, T]:
    """Build a dataset for every authored bundle locale, plus a derived en-US.

    Discovers all ``locales/<dataset>/*.json`` bundles, builds each with
    ``builder(locale, bundle)``, and adds a derived ``en-US`` from the ``en-GB``
    bundle when no ``en-US`` bundle is authored. Adding a locale is therefore a
    matter of adding a bundle file.
    """

    datasets: dict[str, T] = {}
    en_gb: LocaleBundle | None = None
    for locale in available_locales(anchor, dataset):
        bundle = load_bundle(anchor, dataset, locale)
        datasets[locale] = builder(locale, bundle)
        if locale == "en-GB":
            en_gb = bundle
    if en_gb is not None and "en-US" not in datasets:
        datasets["en-US"] = builder("en-US", americanize(en_gb))
    return datasets
