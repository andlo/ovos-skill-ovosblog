"""Smoke tests + index caching (ported pattern from the other providers)."""
import json
import time

from conftest import OVOSBlog, FeedFetchError


def test_imports_cleanly():
    assert OVOSBlog is not None
    assert issubclass(FeedFetchError, Exception)


def test_ovosblog_is_an_ovos_skill():
    from ovos_workshop.skills import OVOSSkill
    assert issubclass(OVOSBlog, OVOSSkill)


def test_refresh_index_uses_fresh_cache_without_scraping(skill):
    cache_file = skill._index_cache_filename()
    (skill.file_system.base / cache_file).write_text(
        json.dumps({"timestamp": time.time(), "index": {"https://x/y": {"title": "Cached"}}})
    )
    skill.fetch_feed_index = lambda: (_ for _ in ()).throw(AssertionError("should not fetch when cache is fresh"))

    skill.refresh_index()

    assert skill.index == {"https://x/y": {"title": "Cached"}}


def test_refresh_index_falls_back_to_stale_cache_on_fetch_failure(skill):
    cache_file = skill._index_cache_filename()
    stale_timestamp = time.time() - skill.INDEX_CACHE_TTL - 1000
    (skill.file_system.base / cache_file).write_text(
        json.dumps({"timestamp": stale_timestamp, "index": {"https://x/old": {"title": "Old"}}})
    )

    def fail():
        raise FeedFetchError("network down")
    skill.fetch_feed_index = fail

    skill.refresh_index()

    assert skill.index == {"https://x/old": {"title": "Old"}}
