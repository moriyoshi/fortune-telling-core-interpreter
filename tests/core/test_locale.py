import pytest
from fortune_telling_core.errors import ValidationError

from fortune_telling_core._locale import normalize_locale, resolve_locale


@pytest.mark.parametrize(
    ("raw", "expected"),
    (
        ("en-us", "en-US"),
        ("en_US", "en-US"),
        ("EN-gb", "en-GB"),
        ("en_US.UTF-8", "en-US"),
        ("ja_JP.UTF-8@calendar=japanese", "ja-JP"),
        ("zh", "zh-CN"),
        ("ko", "ko-KR"),
        ("pt-br", "pt-BR"),
    ),
)
def test_normalize_locale(raw: str, expected: str) -> None:
    assert normalize_locale(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    (
        ("fr", "fr-FR"),
        ("ja", "ja-JP"),
        ("JA", "ja-JP"),
        ("en", "en-GB"),
        ("zh", "zh-CN"),
        ("ko", "ko-KR"),
        ("pt", "pt-BR"),
        ("es", "es-ES"),
        ("ta", "ta-IN"),
        ("ru", "ru-RU"),
        ("de", "de-DE"),
    ),
)
def test_bare_language_code_maps_to_default_locale(raw: str, expected: str) -> None:
    assert normalize_locale(raw) == expected


def test_unsupported_bare_language_passes_through() -> None:
    # An ISO 639 code without a supported territory is accepted, not rejected;
    # it simply resolves to no dataset.
    assert normalize_locale("nl") == "nl"


def test_resolve_locale_includes_explicit_fallbacks() -> None:
    assert resolve_locale("en-US").candidates == ("en-US", "en-GB")
    assert resolve_locale("fr-FR").candidates == ("fr-FR",)


def test_resolve_locale_accepts_bare_language() -> None:
    resolution = resolve_locale("fr")
    assert resolution.requested == "fr"
    assert resolution.normalized == "fr-FR"
    assert resolution.candidates == ("fr-FR",)


def test_malformed_locale_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        normalize_locale("zh-Hant-TW")


def test_posix_locale_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        normalize_locale("C.UTF-8")
