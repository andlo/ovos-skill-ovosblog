"""Tests for _load_collection_aliases() against the real locale/<lang>/
collection.voc files, and the fallback-to-English behavior for any
device language we haven't bothered translating aliases for (this
provider works on ANY language via translation, unlike andersen-tales/
grimm-tales's fixed SUPPORTED_LANGUAGES set - see
ovos-common-reading-pipeline-plugin#26)."""
import pytest


@pytest.mark.parametrize("lang", ["en-us", "da-dk", "de-de", "es-es", "fr-fr", "it-it", "nl-nl", "pt-pt"])
def test_load_collection_aliases_per_language(skill, monkeypatch, lang):
    monkeypatch.setattr(type(skill), "lang", lang, raising=False)

    skill._load_collection_aliases()

    assert len(skill._collection_aliases) > 0
    assert all(isinstance(a, str) for a in skill._collection_aliases)


def test_danish_alias_matches_danish_phrasing(skill, monkeypatch):
    """Regression guard for the actual bug this fixes: a Danish
    collection_hint should match Danish phrasing, not just English."""
    monkeypatch.setattr(type(skill), "lang", "da-dk", raising=False)
    skill._load_collection_aliases()

    assert skill._matches_collection_hint("ovos nyheder") is True


def test_falls_back_to_english_for_untranslated_language(skill, monkeypatch):
    """Japanese has no locale/ja-jp/collection.voc and no close relative
    to fall back to via langcodes - _load_collection_aliases() should
    use FALLBACK_COLLECTION_ALIASES rather than leave collection_hint
    matching completely broken."""
    monkeypatch.setattr(type(skill), "lang", "ja-jp", raising=False)

    skill._load_collection_aliases()

    assert skill._collection_aliases == [
        "openvoiceos blog", "ovos blog", "open voice os blog", "the openvoiceos blog"
    ]
