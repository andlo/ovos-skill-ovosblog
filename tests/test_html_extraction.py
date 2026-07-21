"""Tests for extract_paragraphs() - includes a regression case for a real
bug found while testing against the live feed: stripping <code> entirely
broke sentence grammar ('exists to make the unglamorous part uneventful.'
was missing its subject, 'ovos-installer', which was wrapped in <code>)."""
from conftest import OVOSBlog

SAMPLE_HTML = """
<h1>Boring installs, now on macOS</h1>
<p>The unglamorous part is everything around it.</p>
<p><code>ovos-installer</code> exists to make the unglamorous part uneventful.</p>
<ul>
<li><strong>Method:</strong> <code>virtualenv</code> (only)</li>
<li><strong>Channel:</strong> <code>alpha</code> (only)</li>
</ul>
<pre><code class="hljs language-bash">xcode-select --install
</code></pre>
<p>That's the last paragraph.</p>
"""


def test_extract_paragraphs_keeps_inline_code_as_sentence_text():
    paragraphs = OVOSBlog.extract_paragraphs(SAMPLE_HTML)
    assert "ovos-installer exists to make the unglamorous part uneventful." in paragraphs


def test_extract_paragraphs_keeps_list_items_with_inline_code():
    paragraphs = OVOSBlog.extract_paragraphs(SAMPLE_HTML)
    assert "Method: virtualenv (only)" in paragraphs
    assert "Channel: alpha (only)" in paragraphs


def test_extract_paragraphs_drops_full_code_blocks():
    paragraphs = OVOSBlog.extract_paragraphs(SAMPLE_HTML)
    joined = " ".join(paragraphs)
    assert "xcode-select" not in joined


def test_extract_paragraphs_includes_headings_and_trailing_text():
    paragraphs = OVOSBlog.extract_paragraphs(SAMPLE_HTML)
    assert paragraphs[0] == "Boring installs, now on macOS"
    assert paragraphs[-1] == "That's the last paragraph."


def test_extract_paragraphs_empty_html_returns_empty_list():
    assert OVOSBlog.extract_paragraphs("") == []
