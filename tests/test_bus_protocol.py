"""Tests for handle_search / handle_fetch_content."""
from unittest.mock import MagicMock

from conftest import COMMON_READING_SEARCH_RESPONSE, COMMON_READING_FETCH_CONTENT_RESPONSE, COMMON_READING_PONG


def make_message(data=None):
    m = MagicMock()
    m.data = data or {}
    m.reply = MagicMock(side_effect=lambda mtype, d: MagicMock(msg_type=mtype, data=d))
    return m


def _sample_index():
    return {
        "https://example.test/a": {"title": "Boring installs on macOS", "author": "Alice",
                                    "html": "<p>Text A.</p>", "pubdate": "Mon, 01 Jan 2024 00:00:00 GMT"},
        "https://example.test/b": {"title": "New release notes", "author": "Bob",
                                    "html": "<p>Text B.</p>", "pubdate": "Wed, 01 Jan 2025 00:00:00 GMT"},
    }


def test_handle_search_matches_by_phrase(skill):
    # default fixture lang is en-us, so titles pass through untranslated
    skill.index = _sample_index()

    skill.handle_search(make_message({"phrase": "boring installs macos"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_READING_SEARCH_RESPONSE
    assert sent.data["content_id"] == "https://example.test/a"
    assert sent.data["title"] == "Boring installs on macOS"
    assert sent.data["author"] == "Alice"
    assert sent.data["source"] == "blog.openvoiceos.org"
    assert sent.data["machine_translated"] is False


def test_handle_search_no_phrase_no_hint_stays_silent(skill):
    skill.index = _sample_index()
    skill.handle_search(make_message({"phrase": None, "collection_hint": None}))
    skill.bus.emit.assert_not_called()


def test_handle_search_surprise_me_picks_latest(skill):
    skill.index = _sample_index()

    skill.handle_search(make_message({"phrase": None, "collection_hint": "ovos blog"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.data["content_id"] == "https://example.test/b"  # the newer one


def test_handle_search_stays_silent_for_unmatched_collection(skill):
    skill.index = _sample_index()
    skill.handle_search(make_message({"phrase": "boring installs", "collection_hint": "grimm"}))
    skill.bus.emit.assert_not_called()


def test_handle_search_stays_silent_for_mismatched_content_type(skill):
    skill.index = _sample_index()
    skill.handle_search(make_message({"phrase": "boring installs", "content_type": "poem"}))
    skill.bus.emit.assert_not_called()


def test_handle_search_responds_for_matching_content_type(skill):
    skill.index = _sample_index()
    skill.handle_search(make_message({"phrase": "boring installs", "content_type": "article"}))
    skill.bus.emit.assert_called_once()


def test_handle_fetch_content_returns_translated_paragraphs(skill):
    skill.index = _sample_index()
    skill._maybe_translate_paragraphs = MagicMock(return_value=(["Texte A."], True))

    skill.handle_fetch_content(make_message({"content_id": "https://example.test/a"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_READING_FETCH_CONTENT_RESPONSE
    assert sent.data["paragraphs"] == ["Texte A."]


def test_handle_fetch_content_unknown_id_returns_empty(skill):
    skill.index = {}
    skill.handle_fetch_content(make_message({"content_id": "nonexistent"}))
    sent = skill.bus.emit.call_args[0][0]
    assert sent.data["paragraphs"] == []


def test_handle_ping_replies_with_pong(skill):
    skill.handle_ping(make_message())

    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_READING_PONG
    assert sent.data["skill_id"] == skill.skill_id
    assert sent.data["collection"] == "the OpenVoiceOS Blog"


def test_handle_ping_does_not_touch_the_index(skill):
    skill.index = None

    skill.handle_ping(make_message())

    skill.bus.emit.assert_called_once()
