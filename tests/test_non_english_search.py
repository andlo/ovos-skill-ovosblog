"""Dedicated tests for the non-English search path - the specific fix
requested: match against *translated* titles (a Danish user says a
Danish phrase), and stay silent (no response at all) if no translator
is available, rather than silently offering English content."""
from unittest.mock import MagicMock

from conftest import OVOSBlog


def _sample_index():
    return {
        "https://x/a": {"title": "Boring installs", "author": "Alice",
                         "html": "<p>A</p>", "pubdate": "Mon, 01 Jan 2024 00:00:00 GMT"},
        "https://x/b": {"title": "New release", "author": "Bob",
                         "html": "<p>B</p>", "pubdate": "Wed, 01 Jan 2025 00:00:00 GMT"},
    }


def make_message(data=None):
    m = MagicMock()
    m.data = data or {}
    m.reply = MagicMock(side_effect=lambda mtype, d: MagicMock(msg_type=mtype, data=d))
    return m


def test_non_english_device_matches_against_translated_titles(skill, monkeypatch):
    monkeypatch.setattr(OVOSBlog, "lang", "da-dk", raising=False)
    skill.index = _sample_index()
    fake_translator = MagicMock()
    translations = {"Boring installs": "Kedelige installationer", "New release": "Ny udgivelse"}
    fake_translator.translate.side_effect = lambda text, target, source: translations[text]
    skill._get_translator = MagicMock(return_value=fake_translator)

    # the user speaks Danish, matching the *Danish* title - this would
    # not match well against the English original at all
    skill.handle_search(make_message({"phrase": "kedelige installationer"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.data["content_id"] == "https://x/a"
    assert sent.data["title"] == "Kedelige installationer"
    assert sent.data["machine_translated"] is True


def test_non_english_device_without_translator_stays_completely_silent(skill, monkeypatch):
    monkeypatch.setattr(OVOSBlog, "lang", "da-dk", raising=False)
    skill.index = _sample_index()
    skill._get_translator = MagicMock(return_value=None)

    skill.handle_search(make_message({"phrase": "kedelige installationer"}))

    skill.bus.emit.assert_not_called()


def test_non_english_device_without_translator_declines_surprise_me_too(skill, monkeypatch):
    monkeypatch.setattr(OVOSBlog, "lang", "da-dk", raising=False)
    skill.index = _sample_index()
    skill._get_translator = MagicMock(return_value=None)

    skill.handle_search(make_message({"phrase": None, "collection_hint": "ovos blog"}))

    skill.bus.emit.assert_not_called()


def test_english_device_never_needs_a_translator(skill, monkeypatch):
    monkeypatch.setattr(OVOSBlog, "lang", "en-us", raising=False)
    skill.index = _sample_index()
    skill._get_translator = MagicMock(side_effect=AssertionError("should never be called for English"))

    skill.handle_search(make_message({"phrase": "boring installs"}))

    skill.bus.emit.assert_called_once()
