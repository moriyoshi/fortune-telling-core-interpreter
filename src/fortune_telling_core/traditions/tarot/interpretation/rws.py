"""Rider-Waite-Smith tarot interpretation datasets across locales.

Card text lives in JSON bundles under ``locales/rws/<locale>.json`` as the
``upright`` and ``reversed`` vocab groups (keyed by card symbol id); there is no
template. Card order and the locale-neutral keyword tokens stay in code. en-GB,
fr-FR, and ja-JP are authored bundles; en-US is derived from en-GB by British ->
American spelling normalization.
"""

from __future__ import annotations

from fortune_telling_core._interpretation_bundle import LocaleBundle, build_all
from fortune_telling_core._interpretation_registry import InterpretationRegistry
from fortune_telling_core.interpretation import (
    InterpretationEntry,
    InterpretationKey,
    MappingInterpretationData,
)

_SOURCE = (
    "A. E. Waite, The Pictorial Key to the Tarot, William Rider & Son, 1911; "
    "Wikisource: https://en.wikisource.org/wiki/The_Pictorial_Key_to_the_Tarot"
)
_ANCHOR = __name__.rpartition(".")[0]

_CARDS: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "tarot.rws.major.the_fool",
        ("beginnings", "trust", "freedom", "potential"),
        ("folly", "carelessness", "risk", "naivety"),
    ),
    (
        "tarot.rws.major.the_magician",
        ("will", "skill", "resourcefulness", "manifestation"),
        ("misuse", "trickery", "delay", "unfocused"),
    ),
    (
        "tarot.rws.major.the_high_priestess",
        ("intuition", "mystery", "wisdom", "secrecy"),
        ("secrets", "concealment", "confusion", "disconnection"),
    ),
    (
        "tarot.rws.major.the_empress",
        ("fertility", "abundance", "care", "creativity"),
        ("dependence", "delay", "vanity", "stagnation"),
    ),
    (
        "tarot.rws.major.the_emperor",
        ("authority", "structure", "leadership", "stability"),
        ("tyranny", "rigidity", "immaturity", "control"),
    ),
    (
        "tarot.rws.major.the_hierophant",
        ("tradition", "counsel", "alliance", "mercy"),
        ("conformity", "weakness", "society", "overkindness"),
    ),
    (
        "tarot.rws.major.the_lovers",
        ("choice", "union", "love", "values"),
        ("disharmony", "temptation", "separation", "indecision"),
    ),
    (
        "tarot.rws.major.the_chariot",
        ("victory", "control", "direction", "willpower"),
        ("conflict", "defeat", "disorder", "force"),
    ),
    (
        "tarot.rws.major.strength",
        ("courage", "patience", "compassion", "mastery"),
        ("weakness", "fear", "excess", "brutality"),
    ),
    (
        "tarot.rws.major.the_hermit",
        ("solitude", "reflection", "guidance", "prudence"),
        ("isolation", "concealment", "mistrust", "withdrawal"),
    ),
    (
        "tarot.rws.major.wheel_of_fortune",
        ("change", "fortune", "cycle", "turning-point"),
        ("instability", "resistance", "setback", "uncertainty"),
    ),
    (
        "tarot.rws.major.justice",
        ("justice", "truth", "accountability", "balance"),
        ("bias", "severity", "complication", "injustice"),
    ),
    (
        "tarot.rws.major.the_hanged_man",
        ("surrender", "pause", "sacrifice", "perspective"),
        ("stagnation", "martyrdom", "delay", "resistance"),
    ),
    (
        "tarot.rws.major.death",
        ("ending", "transition", "renewal", "transformation"),
        ("resistance", "inertia", "fear", "stagnation"),
    ),
    (
        "tarot.rws.major.temperance",
        ("balance", "moderation", "healing", "adaptation"),
        ("excess", "discord", "imbalance", "misalignment"),
    ),
    (
        "tarot.rws.major.the_devil",
        ("bondage", "attachment", "temptation", "materialism"),
        ("release", "obsession", "fear", "detachment"),
    ),
    (
        "tarot.rws.major.the_tower",
        ("upheaval", "revelation", "collapse", "awakening"),
        ("avoidance", "oppression", "delayed-crisis", "fear"),
    ),
    (
        "tarot.rws.major.the_star",
        ("hope", "renewal", "inspiration", "clarity"),
        ("doubt", "discouragement", "loss", "pessimism"),
    ),
    (
        "tarot.rws.major.the_moon",
        ("intuition", "dreams", "uncertainty", "illusion"),
        ("confusion", "deception", "anxiety", "release"),
    ),
    (
        "tarot.rws.major.the_sun",
        ("joy", "success", "clarity", "vitality"),
        ("delay", "overconfidence", "partial-success", "clouded-joy"),
    ),
    (
        "tarot.rws.major.judgement",
        ("awakening", "renewal", "reckoning", "calling"),
        ("denial", "self-doubt", "delay", "avoidance"),
    ),
    (
        "tarot.rws.major.the_world",
        ("completion", "success", "fulfilment", "integration"),
        ("stagnation", "inertia", "incompletion", "fixity"),
    ),
    (
        "tarot.rws.minor.wands.ace",
        ("inspiration", "enterprise", "creation", "potential"),
        ("delay", "false-start", "misdirection", "blocked-energy"),
    ),
    (
        "tarot.rws.minor.wands.two",
        ("planning", "influence", "vision", "choice"),
        ("restlessness", "fear", "surprise", "uncertainty"),
    ),
    (
        "tarot.rws.minor.wands.three",
        ("foresight", "enterprise", "cooperation", "expansion"),
        ("delay", "pride", "setback", "poor-support"),
    ),
    (
        "tarot.rws.minor.wands.four",
        ("harmony", "celebration", "home", "stability"),
        ("postponement", "insecurity", "unfinished", "restlessness"),
    ),
    (
        "tarot.rws.minor.wands.five",
        ("competition", "struggle", "rivalry", "challenge"),
        ("trickery", "avoidance", "discord", "fatigue"),
    ),
    (
        "tarot.rws.minor.wands.six",
        ("victory", "recognition", "good-news", "confidence"),
        ("pride", "delay", "fall", "doubt"),
    ),
    (
        "tarot.rws.minor.wands.seven",
        ("defence", "courage", "persistence", "advantage"),
        ("overwhelm", "hesitation", "embarrassment", "pressure"),
    ),
    (
        "tarot.rws.minor.wands.eight",
        ("speed", "movement", "messages", "action"),
        ("delay", "dispute", "haste", "interruption"),
    ),
    (
        "tarot.rws.minor.wands.nine",
        ("resilience", "guardedness", "preparation", "endurance"),
        ("exhaustion", "suspicion", "rigidity", "weakness"),
    ),
    (
        "tarot.rws.minor.wands.ten",
        ("burden", "responsibility", "pressure", "effort"),
        ("oppression", "release", "overextension", "collapse"),
    ),
    (
        "tarot.rws.minor.wands.page",
        ("message", "enthusiasm", "adventure", "discovery"),
        ("immaturity", "bad-news", "impulsiveness", "unreliable"),
    ),
    (
        "tarot.rws.minor.wands.knight",
        ("action", "travel", "ambition", "boldness"),
        ("haste", "disruption", "impulse", "scattered-energy"),
    ),
    (
        "tarot.rws.minor.wands.queen",
        ("confidence", "warmth", "independence", "vitality"),
        ("jealousy", "temper", "domination", "insecurity"),
    ),
    (
        "tarot.rws.minor.wands.king",
        ("leadership", "vision", "enterprise", "honesty"),
        ("severity", "intolerance", "impulse", "domination"),
    ),
    (
        "tarot.rws.minor.cups.ace",
        ("love", "compassion", "renewal", "abundance"),
        ("blocked-emotion", "instability", "withholding", "emptiness"),
    ),
    (
        "tarot.rws.minor.cups.two",
        ("partnership", "affection", "union", "reconciliation"),
        ("disharmony", "separation", "imbalance", "misunderstanding"),
    ),
    (
        "tarot.rws.minor.cups.three",
        ("friendship", "celebration", "community", "joy"),
        ("excess", "gossip", "overindulgence", "shallowness"),
    ),
    (
        "tarot.rws.minor.cups.four",
        ("apathy", "contemplation", "withdrawal", "reassessment"),
        ("new-interest", "movement", "acceptance", "awakening"),
    ),
    (
        "tarot.rws.minor.cups.five",
        ("loss", "regret", "grief", "disappointment"),
        ("recovery", "forgiveness", "return", "acceptance"),
    ),
    (
        "tarot.rws.minor.cups.six",
        ("memory", "nostalgia", "kindness", "innocence"),
        ("stuck-past", "idealisation", "immaturity", "release"),
    ),
    (
        "tarot.rws.minor.cups.seven",
        ("choices", "fantasy", "imagination", "temptation"),
        ("clarity", "decision", "focus", "discernment"),
    ),
    (
        "tarot.rws.minor.cups.eight",
        ("departure", "search", "release", "disillusionment"),
        ("avoidance", "drifting", "return", "stagnation"),
    ),
    (
        "tarot.rws.minor.cups.nine",
        ("contentment", "wishes", "satisfaction", "pleasure"),
        ("complacency", "excess", "dissatisfaction", "smugness"),
    ),
    (
        "tarot.rws.minor.cups.ten",
        ("happiness", "family", "harmony", "fulfilment"),
        ("disharmony", "tension", "false-harmony", "disappointment"),
    ),
    (
        "tarot.rws.minor.cups.page",
        ("message", "intuition", "imagination", "tenderness"),
        ("immaturity", "fantasy", "moodiness", "unreliable"),
    ),
    (
        "tarot.rws.minor.cups.knight",
        ("romance", "invitation", "artistry", "proposal"),
        ("seduction", "moodiness", "unreality", "disappointment"),
    ),
    (
        "tarot.rws.minor.cups.queen",
        ("compassion", "intuition", "care", "empathy"),
        ("dependence", "overwhelm", "secrecy", "moodiness"),
    ),
    (
        "tarot.rws.minor.cups.king",
        ("calm", "generosity", "wisdom", "emotional-control"),
        ("manipulation", "volatility", "indulgence", "dishonesty"),
    ),
    (
        "tarot.rws.minor.swords.ace",
        ("clarity", "truth", "decision", "breakthrough"),
        ("confusion", "harshness", "misuse", "distortion"),
    ),
    (
        "tarot.rws.minor.swords.two",
        ("stalemate", "choice", "balance", "guardedness"),
        ("confusion", "indecision", "disclosure", "avoidance"),
    ),
    (
        "tarot.rws.minor.swords.three",
        ("sorrow", "separation", "heartbreak", "truth"),
        ("recovery", "release", "resentment", "healing"),
    ),
    (
        "tarot.rws.minor.swords.four",
        ("rest", "retreat", "recovery", "contemplation"),
        ("restlessness", "burnout", "return", "exhaustion"),
    ),
    (
        "tarot.rws.minor.swords.five",
        ("conflict", "defeat", "discord", "hollow-victory"),
        ("reconciliation", "resentment", "shame", "repair"),
    ),
    (
        "tarot.rws.minor.swords.six",
        ("transition", "passage", "recovery", "journey"),
        ("resistance", "delay", "baggage", "stagnation"),
    ),
    (
        "tarot.rws.minor.swords.seven",
        ("strategy", "secrecy", "caution", "resourcefulness"),
        ("exposure", "confession", "poor-planning", "deception"),
    ),
    (
        "tarot.rws.minor.swords.eight",
        ("restriction", "fear", "limitation", "helplessness"),
        ("release", "perspective", "freedom", "acceptance"),
    ),
    (
        "tarot.rws.minor.swords.nine",
        ("anxiety", "remorse", "worry", "distress"),
        ("hope", "release", "despair", "healing"),
    ),
    (
        "tarot.rws.minor.swords.ten",
        ("ending", "ruin", "pain", "finality"),
        ("recovery", "survival", "aftermath", "release"),
    ),
    (
        "tarot.rws.minor.swords.page",
        ("watchfulness", "curiosity", "message", "alertness"),
        ("gossip", "rashness", "spying", "immaturity"),
    ),
    (
        "tarot.rws.minor.swords.knight",
        ("speed", "ambition", "argument", "force"),
        ("recklessness", "aggression", "chaos", "impatience"),
    ),
    (
        "tarot.rws.minor.swords.queen",
        ("clarity", "judgement", "independence", "honesty"),
        ("bitterness", "coldness", "criticism", "severity"),
    ),
    (
        "tarot.rws.minor.swords.king",
        ("authority", "strategy", "truth", "discipline"),
        ("cruelty", "manipulation", "rigidity", "severity"),
    ),
    (
        "tarot.rws.minor.pentacles.ace",
        ("opportunity", "prosperity", "security", "manifestation"),
        ("lost-opportunity", "greed", "poor-planning", "instability"),
    ),
    (
        "tarot.rws.minor.pentacles.two",
        ("adaptation", "balance", "change", "juggling"),
        ("disorder", "overextension", "instability", "poor-priorities"),
    ),
    (
        "tarot.rws.minor.pentacles.three",
        ("skill", "collaboration", "craft", "planning"),
        ("poor-work", "disorganisation", "mediocrity", "misalignment"),
    ),
    (
        "tarot.rws.minor.pentacles.four",
        ("security", "control", "possession", "conservation"),
        ("greed", "rigidity", "fear", "release"),
    ),
    (
        "tarot.rws.minor.pentacles.five",
        ("hardship", "poverty", "exclusion", "worry"),
        ("recovery", "assistance", "hope", "improvement"),
    ),
    (
        "tarot.rws.minor.pentacles.six",
        ("generosity", "charity", "exchange", "fairness"),
        ("debt", "inequality", "strings-attached", "selfishness"),
    ),
    (
        "tarot.rws.minor.pentacles.seven",
        ("patience", "assessment", "harvest", "investment"),
        ("impatience", "poor-return", "waste", "frustration"),
    ),
    (
        "tarot.rws.minor.pentacles.eight",
        ("diligence", "craft", "learning", "discipline"),
        ("carelessness", "monotony", "poor-focus", "shortcuts"),
    ),
    (
        "tarot.rws.minor.pentacles.nine",
        ("self-sufficiency", "comfort", "refinement", "prosperity"),
        ("dependence", "insecurity", "appearance", "setback"),
    ),
    (
        "tarot.rws.minor.pentacles.ten",
        ("legacy", "family", "wealth", "stability"),
        ("instability", "family-tension", "loss", "short-term"),
    ),
    (
        "tarot.rws.minor.pentacles.page",
        ("study", "news", "ambition", "practicality"),
        ("laziness", "poor-planning", "immaturity", "delay"),
    ),
    (
        "tarot.rws.minor.pentacles.knight",
        ("reliability", "patience", "method", "service"),
        ("stubbornness", "stagnation", "routine", "inertia"),
    ),
    (
        "tarot.rws.minor.pentacles.queen",
        ("nurture", "prosperity", "practicality", "security"),
        ("possessiveness", "dependence", "anxiety", "imbalance"),
    ),
    (
        "tarot.rws.minor.pentacles.king",
        ("success", "stewardship", "abundance", "authority"),
        ("greed", "rigidity", "control", "materialism"),
    ),
)


def _build(locale: str, bundle: LocaleBundle) -> MappingInterpretationData:
    upright = bundle.group("upright")
    reversed_text = bundle.group("reversed")
    entries: list[InterpretationEntry] = []
    for symbol_id, upright_keywords, reversed_keywords in _CARDS:
        for variant in (None, "upright"):
            entries.append(
                InterpretationEntry(
                    key=InterpretationKey(symbol_id=symbol_id, variant=variant),
                    text=upright[symbol_id],
                    keywords=upright_keywords,
                    source=_SOURCE,
                )
            )
        entries.append(
            InterpretationEntry(
                key=InterpretationKey(symbol_id=symbol_id, variant="reversed"),
                text=reversed_text[symbol_id],
                keywords=reversed_keywords,
                source=_SOURCE,
            )
        )
    return MappingInterpretationData(id=f"tarot.rws.{locale}.v1", entries=tuple(entries))


_DATASETS = build_all(_ANCHOR, "rws", _build)

RWS_EN_GB = _DATASETS["en-GB"]
RWS_EN_US = _DATASETS["en-US"]
RWS_FR_FR = _DATASETS["fr-FR"]
RWS_JA_JP = _DATASETS["ja-JP"]
RWS_REGISTRY = InterpretationRegistry(_DATASETS)
