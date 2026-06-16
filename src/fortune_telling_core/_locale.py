"""Locale normalization and fallback policy."""

from __future__ import annotations

from dataclasses import dataclass

from fortune_telling_core.errors import ValidationError

SUPPORTED_LOCALES = frozenset(
    {
        "en-GB",
        "en-US",
        "fr-FR",
        "de-DE",
        "zh-CN",
        "zh-TW",
        "ko-KR",
        "pt-BR",
        "es-ES",
        "ja-JP",
        "ru-RU",
        "id-ID",
        "vi-VN",
        "th-TH",
        "hi-IN",
        "bn-IN",
        "te-IN",
        "mr-IN",
        "ta-IN",
    }
)

# Default territory for an ambiguous bare language code, i.e. one with more than
# one supported territory. Single-territory languages are derived automatically.
_LANGUAGE_OVERRIDES = {
    "en": "en-GB",
    "zh": "zh-CN",
}


def _language_defaults() -> dict[str, str]:
    """Map each bare ISO 639 language to its default supported locale."""

    by_language: dict[str, set[str]] = {}
    for tag in SUPPORTED_LOCALES:
        by_language.setdefault(tag.split("-", maxsplit=1)[0], set()).add(tag)
    defaults: dict[str, str] = {}
    for language, tags in by_language.items():
        if language in _LANGUAGE_OVERRIDES:
            defaults[language] = _LANGUAGE_OVERRIDES[language]
        elif len(tags) == 1:
            defaults[language] = next(iter(tags))
    return defaults


# Bare ISO 639 language code -> default supported locale, e.g. "fr" -> "fr-FR".
_LANGUAGE_DEFAULT = _language_defaults()

_FALLBACKS = {
    "en-US": ("en-GB",),
}


@dataclass(frozen=True, slots=True)
class LocaleResolution:
    """Normalized locale request and ordered dataset lookup candidates."""

    requested: str
    normalized: str
    candidates: tuple[str, ...]


def resolve_locale(locale: str) -> LocaleResolution:
    """Normalize a locale tag and return ordered lookup candidates.

    The resolver intentionally covers the project's currently supported locale
    set instead of implementing full BCP 47 negotiation.
    """

    normalized = normalize_locale(locale)
    candidates = (normalized, *_FALLBACKS.get(normalized, ()))
    return LocaleResolution(requested=locale, normalized=normalized, candidates=candidates)


def normalize_locale(locale: str) -> str:
    """Normalize a locale tag such as ``en_us`` to ``en-US``.

    A bare ISO 639 language code with no territory is accepted and mapped to its
    default supported locale: for example ``fr`` -> ``fr-FR`` and ``ja`` -> ``ja-JP``,
    with ``en`` -> ``en-GB`` and ``zh`` -> ``zh-CN`` for the languages that have
    more than one supported territory. A bare language with no supported territory
    is returned lower-cased and simply resolves to no dataset.

    Args:
        locale: Locale tag supplied by a request.

    Returns:
        Canonicalized locale tag.

    Raises:
        ValidationError: If the locale is empty or structurally unsupported.
    """

    value = locale.strip().split(".", maxsplit=1)[0].split("@", maxsplit=1)[0].replace("_", "-")
    if not value:
        raise ValidationError("locale must not be empty")
    if value.upper() in {"C", "POSIX"}:
        raise ValidationError(f"unsupported locale format: {locale}")

    parts = tuple(part for part in value.split("-") if part)
    if len(parts) == 1:
        language = parts[0].lower()
        return _LANGUAGE_DEFAULT.get(language, language)
    if len(parts) != 2:
        raise ValidationError(f"unsupported locale format: {locale}")

    language, region = parts
    if len(language) != 2 or len(region) != 2:
        raise ValidationError(f"unsupported locale format: {locale}")
    return f"{language.lower()}-{region.upper()}"
