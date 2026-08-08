"""FinVADER-Extended, step 1 — mine a financial-news corpus.

Pull article metadata from three publishers via RSS (CNBC + MarketWatch direct,
Reuters via Google News RSS), dedupe on title+url, and save:
  data/lexicon_extension/articles_metadata.json   (the curated record list)
  data/lexicon_extension/articles_metadata.csv     (same, for convenience)
  data/lexicon_extension/corpus_text.txt           (title + lead, for step 2)
  data/lexicon_extension/cache/*.xml               (raw feeds, so reruns are offline)

Raw scraped text is gitignored (same rule as the project's own raw data). Only
the derived candidate-word lists / summary stats (step 2 onward) are committed.

RSS is used because it is published for consumption. Requests carry a descriptive
User-Agent and are rate-limited (1s between calls).
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import pathlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
RAW = ROOT / "data" / "lexicon_extension"          # gitignored raw corpus
PUB = ROOT / "results" / "lexicon"                 # committed derived artifacts
CACHE = RAW / "cache"
for _d in (RAW, PUB, CACHE):
    _d.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "FINS3645-student-research/1.0 "
                    "(academic coursework; contact z5589978@ad.unsw.edu.au)"}
RATE_LIMIT_S = 1.0

# ── Feed registry: (publisher, category, source_feed, url) ────────────────────
CNBC = "https://www.cnbc.com/id/{}/device/rss/rss.html"
GNEWS = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

FEEDS = [
    # CNBC direct RSS (documented category feed IDs)
    ("CNBC", "Top News",  "cnbc_rss", CNBC.format("100003114")),
    ("CNBC", "Markets",   "cnbc_rss", CNBC.format("20910258")),
    ("CNBC", "Finance",   "cnbc_rss", CNBC.format("10000664")),
    ("CNBC", "Earnings",  "cnbc_rss", CNBC.format("15839135")),
    ("CNBC", "Business",  "cnbc_rss", CNBC.format("10001147")),
    ("CNBC", "Investing", "cnbc_rss", CNBC.format("15839069")),
    # MarketWatch direct RSS
    ("MarketWatch", "Top Stories",    "mw_rss", "http://feeds.marketwatch.com/marketwatch/topstories/"),
    ("MarketWatch", "Real-time",      "mw_rss", "http://feeds.marketwatch.com/marketwatch/realtimeheadlines/"),
    ("MarketWatch", "Market Pulse",   "mw_rss", "http://feeds.marketwatch.com/marketwatch/marketpulse/"),
    ("MarketWatch", "Bulletins",      "mw_rss", "http://feeds.marketwatch.com/marketwatch/bulletins/"),
    # Reuters via Google News RSS (Reuters has no working public RSS of its own)
    ("Reuters", "Markets",  "googlenews", GNEWS.format("site:reuters.com%20(markets%20OR%20stocks%20OR%20shares)%20when:21d")),
    ("Reuters", "Business", "googlenews", GNEWS.format("site:reuters.com%20(business%20OR%20earnings%20OR%20revenue)%20when:21d")),
    ("Reuters", "Economy",  "googlenews", GNEWS.format("site:reuters.com%20(economy%20OR%20Fed%20OR%20inflation%20OR%20rates)%20when:21d")),
]

_TAG = re.compile(r"<[^>]+>")


def _clean(text: str, publisher: str) -> str:
    """Unescape entities, strip HTML, and drop a trailing ' - Publisher' suffix."""
    text = html.unescape(text or "").strip()
    text = _TAG.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Google News appends ' - Reuters' (or other source) to titles; drop it.
    text = re.sub(rf"\s*[-–—]\s*{re.escape(publisher)}\s*$", "", text)
    return text.strip()


def _fetch(url: str) -> str | None:
    """Fetch a feed, caching the raw XML so reruns don't re-hit the site."""
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    cache_file = CACHE / f"{key}.xml"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="ignore")
    try:
        r = requests.get(url, headers=UA, timeout=20)
        r.raise_for_status()
        cache_file.write_text(r.text, encoding="utf-8")
        time.sleep(RATE_LIMIT_S)
        return r.text
    except Exception as exc:
        print(f"    ! fetch failed: {type(exc).__name__} for {url[:70]}")
        return None


def _parse_items(xml_text: str, publisher: str, category: str, source_feed: str) -> list[dict]:
    """Parse RSS <item> elements into metadata records."""
    records = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return records
    for item in root.iter("item"):
        title = _clean(item.findtext("title", ""), publisher)
        link = (item.findtext("link", "") or "").strip()
        desc = _clean(item.findtext("description", ""), publisher)
        pub_raw = (item.findtext("pubDate", "") or "").strip()
        try:
            pub_iso = parsedate_to_datetime(pub_raw).astimezone(timezone.utc).isoformat() if pub_raw else ""
        except Exception:
            pub_iso = ""
        if not title:
            continue
        records.append({
            "title": title,
            "url": link,
            "published_date": pub_iso,
            "published_raw": pub_raw,
            "publisher": publisher,
            "category": category,
            "source_feed": source_feed,
            "lead": desc,
            "scrape_timestamp": datetime.now(timezone.utc).isoformat(),
        })
    return records


def main() -> None:
    print("=== FinVADER-Extended step 1: scrape corpus ===")
    all_records: list[dict] = []
    per_source: dict[str, int] = {}
    for publisher, category, source_feed, url in FEEDS:
        xml_text = _fetch(url)
        if not xml_text:
            continue
        recs = _parse_items(xml_text, publisher, category, source_feed)
        per_source[publisher] = per_source.get(publisher, 0) + len(recs)
        print(f"  {publisher:<12} {category:<14} {len(recs):>3} items")
        all_records.extend(recs)

    # Dedupe on (normalised title, url)
    seen = set()
    unique = []
    for r in all_records:
        key = (r["title"].lower(), r["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    print(f"\n  raw items:    {len(all_records)}")
    print(f"  unique items: {len(unique)}  (deduped on title+url)")
    print("  by publisher (pre-dedupe):", per_source)

    # Raw metadata JSON stays gitignored under data/. (No CSV copy: the course
    # check_handin forbids .csv outside results/, so the committable copy is the
    # summary below; load the JSON with pandas.read_json if a frame is needed.)
    (RAW / "articles_metadata.json").write_text(
        json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8")
    df = pd.DataFrame(unique)

    # Corpus text = title + lead (richer vocabulary than titles alone) — raw, gitignored
    corpus_lines = [f"{r['title']} {r['lead']}".strip() for r in unique]
    (RAW / "corpus_text.txt").write_text("\n".join(corpus_lines), encoding="utf-8")

    # Committable summary (no raw text) — publisher / category counts
    summary = (df.groupby(["publisher", "category"]).size()
                 .rename("n_articles").reset_index())
    summary.to_csv(PUB / "corpus_summary.csv", index=False)

    print(f"\n  saved articles_metadata.json, corpus_text.txt (raw, gitignored)")
    print(f"  saved results/lexicon/corpus_summary.csv (committable)")
    print(f"\n  UNIQUE ARTICLES: {len(unique)}")
    return len(unique)


if __name__ == "__main__":
    main()
