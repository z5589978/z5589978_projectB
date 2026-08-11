"""FinVADER-Extended idioms — grow the corpus for phrase (idiom) mining.

Expands the news pull with many finance-topic Google News queries (site-restricted
to major finance outlets) plus the CNBC/MarketWatch direct feeds, unions with the
existing article metadata, dedupes on title+url, and writes a larger corpus for
idiom candidate extraction:

  data/lexicon_extension/corpus_text_idioms.txt        (title + lead, per article)
  data/lexicon_extension/articles_metadata_idioms.json (metadata, gitignored)
  results/lexicon/corpus_idioms_summary.csv            (committable counts)

Raw feeds cached under data/lexicon_extension/cache/. RSS only, descriptive UA,
rate-limited. The idiom corpus is used only to DISCOVER phrases; all reported
sentiment results still run on the provided news_headlines.parquet.
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
RAW = ROOT / "data" / "lexicon_extension"
PUB = ROOT / "results" / "lexicon"
CACHE = RAW / "cache"
for d in (RAW, PUB, CACHE):
    d.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "FINS3645-student-research/1.0 (academic coursework; contact z5589978@ad.unsw.edu.au)"}
RATE = 1.0
GNEWS = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"
CNBC = "https://www.cnbc.com/id/{}/device/rss/rss.html"

SITES = "(site:reuters.com OR site:cnbc.com OR site:marketwatch.com OR site:bloomberg.com)"
TOPICS = [
    "earnings beat", "earnings miss", "profit warning", "guidance cut",
    "raises guidance", "dividend increase", "share buyback", "merger acquisition",
    "ipo debut", "analyst downgrade", "analyst upgrade", "bankruptcy filing",
    "layoffs jobs", "record high", "record low", "stocks selloff", "wall street rally",
    "rate hike", "rate cut", "inflation data", "recession fears", "oil prices",
    "bond yields", "short squeeze", "revenue growth", "profit surge", "stock plunge",
    "cost cutting", "supply chain", "market volatility",
]
FEEDS = [("gnews", GNEWS.format(requests.utils.quote(f"{SITES} {t} when:60d"))) for t in TOPICS]
FEEDS += [("cnbc", CNBC.format(i)) for i in
          ["100003114", "20910258", "10000664", "15839135", "10001147", "15839069"]]
FEEDS += [("mw", u) for u in [
    "http://feeds.marketwatch.com/marketwatch/topstories/",
    "http://feeds.marketwatch.com/marketwatch/marketpulse/",
    "http://feeds.marketwatch.com/marketwatch/realtimeheadlines/",
]]

_TAG = re.compile(r"<[^>]+>")


def clean(t: str) -> str:
    t = _TAG.sub(" ", html.unescape(t or "")).strip()
    t = re.sub(r"\s+", " ", t)
    return re.sub(r"\s*[-–—]\s*[A-Z][A-Za-z.]+\s*$", "", t).strip()


def fetch(url: str) -> str | None:
    cf = CACHE / (hashlib.md5(url.encode()).hexdigest()[:12] + ".xml")
    if cf.exists():
        return cf.read_text(encoding="utf-8", errors="ignore")
    try:
        r = requests.get(url, headers=UA, timeout=25); r.raise_for_status()
        cf.write_text(r.text, encoding="utf-8"); time.sleep(RATE); return r.text
    except Exception as e:
        print(f"    ! {type(e).__name__} {url[:60]}"); return None


def parse(xml: str, src: str) -> list[dict]:
    out = []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return out
    for it in root.iter("item"):
        title = clean(it.findtext("title", ""))
        if not title:
            continue
        out.append({"title": title, "url": (it.findtext("link", "") or "").strip(),
                    "lead": clean(it.findtext("description", "")), "source_feed": src,
                    "scrape_timestamp": datetime.now(timezone.utc).isoformat()})
    return out


def main() -> None:
    print("=== idiom corpus: expanded scrape ===")
    recs = []
    existing = RAW / "articles_metadata.json"
    if existing.exists():
        recs.extend(json.loads(existing.read_text()))
        print(f"  seeded from existing word corpus: {len(recs)} articles")
    for src, url in FEEDS:
        xml = fetch(url)
        if xml:
            recs.extend(parse(xml, src))
    seen, uniq = set(), []
    for r in recs:
        k = (r["title"].lower(), r.get("url", ""))
        if k not in seen:
            seen.add(k); uniq.append(r)
    print(f"  total unique articles (idiom corpus): {len(uniq)}")

    (RAW / "articles_metadata_idioms.json").write_text(json.dumps(uniq, ensure_ascii=False))
    lines = [f"{r['title']} {r.get('lead','')}".strip() for r in uniq]
    (RAW / "corpus_text_idioms.txt").write_text("\n".join(lines), encoding="utf-8")
    pd.Series([r["source_feed"] for r in uniq]).value_counts().rename_axis("source_feed")\
        .reset_index(name="n_articles").to_csv(PUB / "corpus_idioms_summary.csv", index=False)
    print(f"  saved corpus_text_idioms.txt (raw), corpus_idioms_summary.csv (committable)")


if __name__ == "__main__":
    main()
