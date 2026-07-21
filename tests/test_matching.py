"""Tests for fuzzy collection_hint and content_type matching."""
import pytest


@pytest.mark.parametrize("hint", [
    "openvoiceos blog", "OVOS blog", "open voice os blog", "the openvoiceos blog",
])
def test_matches_known_collection_aliases(skill, hint):
    assert skill._matches_collection_hint(hint) is True


@pytest.mark.parametrize("hint", ["grimm", "andersen", "andrew lang"])
def test_does_not_match_other_collections(skill, hint):
    assert skill._matches_collection_hint(hint) is False


def test_none_collection_hint_matches_everyone(skill):
    assert skill._matches_collection_hint(None) is True


@pytest.mark.parametrize("content_type", ["article", "blog", "news", "post", "ARTICLE"])
def test_matches_known_content_types(skill, content_type):
    assert skill._matches_content_type(content_type) is True


@pytest.mark.parametrize("content_type", ["story", "poem", "recipe"])
def test_does_not_match_other_content_types(skill, content_type):
    assert skill._matches_content_type(content_type) is False


def test_none_content_type_matches_everyone(skill):
    assert skill._matches_content_type(None) is True
