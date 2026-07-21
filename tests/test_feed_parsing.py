"""Tests for feed fetching/parsing and _latest_link()."""
from unittest.mock import MagicMock

import pytest
import requests
from conftest import OVOSBlog, FeedFetchError

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0"><channel>
<title>OpenVoiceOS Blog</title>
<item>
  <title>Older Post</title>
  <link>https://example.test/older</link>
  <guid>https://example.test/older</guid>
  <dc:creator>Alice</dc:creator>
  <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
  <description><![CDATA[<p>Older content.</p>]]></description>
</item>
<item>
  <title>Newer Post</title>
  <link>https://example.test/newer</link>
  <guid>https://example.test/newer</guid>
  <dc:creator>Bob</dc:creator>
  <pubDate>Wed, 01 Jan 2025 00:00:00 GMT</pubDate>
  <description><![CDATA[<p>Newer content.</p>]]></description>
</item>
</channel></rss>"""


def test_fetch_feed_index_parses_items(skill, monkeypatch):
    fake_response = MagicMock(content=SAMPLE_FEED.encode("utf-8"))
    fake_response.raise_for_status = MagicMock()
    monkeypatch.setattr(requests, "get", lambda *a, **kw: fake_response)

    index = skill.fetch_feed_index()

    assert len(index) == 2
    assert index["https://example.test/older"]["title"] == "Older Post"
    assert index["https://example.test/older"]["author"] == "Alice"
    assert "<p>Older content.</p>" in index["https://example.test/older"]["html"]


def test_fetch_feed_index_network_error_raises(skill, monkeypatch):
    def fail(*a, **kw):
        raise requests.ConnectionError("boom")
    monkeypatch.setattr(requests, "get", fail)

    with pytest.raises(FeedFetchError):
        skill.fetch_feed_index()


def test_fetch_feed_index_bad_xml_raises(skill, monkeypatch):
    fake_response = MagicMock(content=b"not xml at all <<<")
    fake_response.raise_for_status = MagicMock()
    monkeypatch.setattr(requests, "get", lambda *a, **kw: fake_response)

    with pytest.raises(FeedFetchError):
        skill.fetch_feed_index()


def test_latest_link_picks_most_recent_pubdate(skill, monkeypatch):
    fake_response = MagicMock(content=SAMPLE_FEED.encode("utf-8"))
    fake_response.raise_for_status = MagicMock()
    monkeypatch.setattr(requests, "get", lambda *a, **kw: fake_response)
    skill.index = skill.fetch_feed_index()

    latest = skill._latest_link()

    assert latest == "https://example.test/newer"
