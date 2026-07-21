"""Tests for the translation fallback logic - this is the behavior the
user specifically asked for: translate when needed, disclose it, and
degrade gracefully (serve English, no false disclosure) if no
translation plugin is available."""
from unittest.mock import MagicMock


def test_maybe_translate_text_skips_english(skill):
    text, translated = skill._maybe_translate_text("Hello", "en-us")
    assert text == "Hello"
    assert translated is False


def test_maybe_translate_text_translates_when_plugin_available(skill):
    fake_translator = MagicMock()
    fake_translator.translate.return_value = "Bonjour"
    skill._get_translator = MagicMock(return_value=fake_translator)

    text, translated = skill._maybe_translate_text("Hello", "fr-fr")

    assert text == "Bonjour"
    assert translated is True
    fake_translator.translate.assert_called_once_with("Hello", target="fr", source="en")


def test_maybe_translate_text_falls_back_when_no_plugin(skill):
    skill._get_translator = MagicMock(return_value=None)

    text, translated = skill._maybe_translate_text("Hello", "fr-fr")

    assert text == "Hello"
    assert translated is False


def test_maybe_translate_text_falls_back_on_translator_error(skill):
    fake_translator = MagicMock()
    fake_translator.translate.side_effect = RuntimeError("service down")
    skill._get_translator = MagicMock(return_value=fake_translator)

    text, translated = skill._maybe_translate_text("Hello", "fr-fr")

    assert text == "Hello"
    assert translated is False


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


def test_get_translator_caches_failure_without_retrying(skill, monkeypatch):
    import ovos_plugin_manager.language as lang_mod
    monkeypatch.setattr(
        lang_mod.OVOSLangTranslationFactory, "create",
        MagicMock(side_effect=ValueError("no plugin")),
    )

    assert skill._get_translator() is None
    assert skill._translator_failed is True
    # second call should not attempt to create again (no new exception raised)
    assert skill._get_translator() is None
