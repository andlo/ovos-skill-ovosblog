# <img src='rss-512.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> OVOS Blog

A *provider* skill for [ovos-common-reading-pipeline-plugin](https://github.com/andlo/ovos-common-reading-pipeline-plugin),
reading the [OpenVoiceOS blog](https://blog.openvoiceos.org/) aloud.

This exists to prove a point: **common-reading isn't just for fairy
tales.** It's an "article" provider, not a storyteller.

[![Tests](https://github.com/andlo/ovos-skill-ovosblog/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-ovosblog/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-ovosblog.svg)](https://pypi.org/project/ovos-skill-ovosblog/)

> **This skill has no standalone voice interface.** It registers no
> intents and never speaks. It only answers
> [ovos.common_reading.* bus messages](https://github.com/andlo/ovos-common-reading-pipeline-plugin#the-ovoscommon_reading-bus-protocol),
> so you also need **ovos-common-reading-pipeline-plugin** installed and
> added to your pipeline config for it to be useful at all.

## Install
```bash
pip install ovos-skill-ovosblog ovos-common-reading-pipeline-plugin
```

## Source

Feeds from https://blog.openvoiceos.org/feed.xml (RSS 2.0). The feed
already contains full article HTML in `<description>`, not just a
summary, so no separate page fetch is needed - just the feed itself
(refreshed at most once an hour, matching the feed's own `<ttl>60</ttl>`).

## Translation

The feed is English-only. If the device language isn't English, this
provider machine-translates:
- **titles**, before matching a spoken phrase against them (a Danish
  user speaks a Danish phrase, so that's what has to be matched - not
  the English original), and
- the **full article text**, when actually reading it aloud.

using whatever [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager)
language-translation plugin is configured
(`OVOSLangTranslationFactory.create()`).

Every search response includes a `"machine_translated": true/false`
field - `ovos-common-reading-pipeline-plugin` is expected to disclose this before
reading the content aloud, so users know it's a machine translation
rather than an original-language text.

**If no translation plugin is installed/configured, this provider does
not respond to searches at all for a non-English device** - it would be
misleading to offer an article it can only actually deliver in English
when the user asked in (and expects) their own language. (English
devices never need a translator and always get a response.)

## Collection hints

Responds to `collection_hint` values like "openvoiceos blog", "ovos
blog", "open voice os blog".

## Content type

Responds to `content_type` hints of "article", "blog", "news", or "post".
Ignores everything else (e.g. "story", "poem").

## "Surprise me"

A search with no specific `phrase` but a matching `collection_hint`
(e.g. "read me something from the OVOS blog") returns the **most
recent** post, by `pubDate`.

## Credits

Content and feed from [blog.openvoiceos.org](https://blog.openvoiceos.org/),
maintained by the OpenVoiceOS community.

## Category
**News**

## Tags
#news #blog #openvoiceos #rss #provider
