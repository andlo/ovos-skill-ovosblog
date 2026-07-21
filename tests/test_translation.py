"""Tests for translation - this is the behavior the user specifically
asked for: match against *translated* titles (not English ones), and
decline to offer anything in a language we can't actually deliver rather
than silently falling back to English."""
from unittest.mock import MagicMock


def _sample_index():
    return {
        "https://x/a": {"title": "Boring installs", "author": "Alice",
                         "html": "<p>A</p>", "pubdate": "Mon, 01 Jan 2024 00:00:00 GMT"},
        "https://x/b": {"title": "New release", "author": "Bob",
                         "html": "<p>B</p>", "pubdate": "Wed, 01 Jan 2025 00:00:00 GMT"},
    }


def test_get_translated_titles_english_returns_originals_unchanged(skill):
    skill.index = _sample_index()
    titles = skill._get_translated_titles("en-us")
    assert titles == {"https://x/a": "Boring installs", "https://x/b": "New release"}


def test_get_translated_titles_translates_all_titles(skill):
    skill.index = _sample_index()
    fake_translator = MagicMock()
    fake_translator.translate.side_effect = lambda text, target, source: f"[{target}] {text}"
    skill._get_translator = MagicMock(return_value=fake_translator)

    titles = skill._get_translated_titles("da-dk")

    assert titles == {"https://x/a": "[da] Boring installs", "https://x/b": "[da] New release"}
    assert fake_translator.translate.call_count == 2


def test_get_translated_titles_returns_none_without_translator(skill):
    skill.index = _sample_index()
    skill._get_translator = MagicMock(return_value=None)
    assert skill._get_translated_titles("da-dk") is None


def test_get_translated_titles_returns_none_on_translation_failure(skill):
    skill.index = _sample_index()
    fake_translator = MagicMock()
    fake_translator.translate.side_effect = RuntimeError("service down")
    skill._get_translator = MagicMock(return_value=fake_translator)

    assert skill._get_translated_titles("da-dk") is None


def test_get_translated_titles_caches_per_language(skill):
    skill.index = _sample_index()
    fake_translator = MagicMock()
    fake_translator.translate.side_effect = lambda text, target, source: f"[{target}] {text}"
    skill._get_translator = MagicMock(return_value=fake_translator)

    first = skill._get_translated_titles("da-dk")
    second = skill._get_translated_titles("da-dk")

    assert first == second
    assert fake_translator.translate.call_count == 2  # not called again on the second request


def test_maybe_translate_paragraphs_translates_each_one(skill):
    fake_translator = MagicMock()
    fake_translator.translate.side_effect = lambda text, target, source: f"[{target}] {text}"
    skill._get_translator = MagicMock(return_value=fake_translator)

    paragraphs, translated = skill._maybe_translate_paragraphs(["One.", "Two."], "da-dk")

    assert paragraphs == ["[da] One.", "[da] Two."]
    assert translated is True


def test_maybe_translate_paragraphs_skips_english(skill):
    paragraphs, translated = skill._maybe_translate_paragraphs(["One.", "Two."], "en-us")
    assert paragraphs == ["One.", "Two."]
    assert translated is False


def test_maybe_translate_paragraphs_falls_back_on_error(skill):
    fake_translator = MagicMock()
    fake_translator.translate.side_effect = RuntimeError("service down")
    skill._get_translator = MagicMock(return_value=fake_translator)

    paragraphs, translated = skill._maybe_translate_paragraphs(["One."], "da-dk")

    assert paragraphs == ["One."]
    assert translated is False


def test_get_translator_caches_failure_without_retrying(skill, monkeypatch):
    import ovos_plugin_manager.language as lang_mod
    monkeypatch.setattr(
        lang_mod.OVOSLangTranslationFactory, "create",
        MagicMock(side_effect=ValueError("no plugin")),
    )

    assert skill._get_translator() is None
    assert skill._translator_failed is True
    assert skill._get_translator() is None
