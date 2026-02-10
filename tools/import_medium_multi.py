#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import time
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FEEDS_FILE = ROOT / "tools" / "medium_feeds.txt"
TRACK_FILE = ROOT / "medium_imported_urls.txt"

SECTION_DIRS = {
    "teardown": ROOT / "content" / "teardown",
    "shenzhen": ROOT / "content" / "shenzhen",
    "fabcross": ROOT / "content" / "fabcross",
    "archive": ROOT / "content" / "archive",
}

# 「どのfeedから来たか」で確定（publication判定が一番強い）
FEED_TO_SECTION = {
    "https://medium.com/feed/bunkai": "teardown",
    "https://medium.com/feed/%E5%88%86%E8%A7%A3%E3%81%AE%E3%82%B9%E3%82%B9%E3%83%A1": "teardown",
    "https://medium.com/feed/shenzhen-high-tour-by-makers": "shenzhen",
    "https://medium.com/feed/fabcross%E9%81%8E%E5%8E%BB%E9%80%A3%E8%BC%89": "fabcross",
    "https://medium.com/feed/%E3%83%96%E3%83%AD%E3%83%9E%E3%82%AC%E9%81%8E%E5%8E%BB%E8%A8%98%E4%BA%8B%E3%82%B5%E3%83%AB%E3%83%99%E3%83%BC%E3%82%B8": "archive",
    "https://medium.com/feed/ecosystembymakers": "archive",
    # profile feed は混ざるので archive に落とす（あとでタグで振り分け）
    "https://tks.medium.com/feed": "archive",
    "https://medium.com/@tks/feed": "archive",
}

MONTHLY_WORD = "月次報告"
MONTHLY_TAG = "monthly-report"

UA = "Mozilla/5.0 (compatible; MediumImporter/2.0)"


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("ttps://"):
        url = "h" + url
    url = url.split("?")[0].split("#")[0].strip()
    return url.rstrip("/")


def extract_post_id_from_guid(guid: str) -> str | None:
    """
    RSSの <guid> が https://medium.com/p/<hex> 形式なのでそこから取る
    """
    if not guid:
        return None
    m = re.search(r"medium\.com/p/([0-9a-f]{6,})", guid)
    return m.group(1) if m else None


def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "post"


def norm_tag(t: str) -> str:
    t = (t or "").strip().lower()
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"[^a-z0-9\-\u3040-\u30ff\u4e00-\u9fff]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t


def parse_rss(xml_text: str) -> list[dict]:
    """
    returns list of items: {title, link, guid, pubDate, categories[], content_html}
    """
    items: list[dict] = []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return items

    # Medium RSS uses namespaces
    ns = {
        "content": "http://purl.org/rss/1.0/modules/content/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "atom": "http://www.w3.org/2005/Atom",
    }

    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        guid = (it.findtext("guid") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()

        cats = []
        for c in it.findall("category"):
            if c.text and c.text.strip():
                cats.append(c.text.strip())

        content_el = it.find("content:encoded", ns)
        content_html = (content_el.text or "").strip() if content_el is not None else ""

        items.append(
            {
                "title": title,
                "link": link,
                "guid": guid,
                "pubDate": pub,
                "categories": cats,
                "content_html": content_html,
            }
        )
    return items


def http_get(url: str, timeout=30) -> str:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_pubdate_to_iso(pubdate: str) -> str:
    # example: Tue, 10 Feb 2026 05:28:47 GMT
    try:
        dt = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return ""


def html_to_md(html: str) -> str:
    """
    超ざっくり変換（RSS本文はHTMLなので、まずは最低限でOK）
    改善したければ: GH Actionsで 'pip install html2text' して html2text に差し替え可能。
    """
    # remove Medium tracking image
    html = re.sub(r'<img[^>]+medium\.com/_/stat[^>]*>', "", html, flags=re.I)
    # remove "Originally published in..." block
    html = re.sub(r"<hr>.*$", "", html, flags=re.I | re.S)

    # very rough: convert paragraphs and links
    html = re.sub(r"</p>\s*<p>", "\n\n", html, flags=re.I)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"<p[^>]*>", "", html, flags=re.I)
    html = re.sub(r"</p>", "", html, flags=re.I)

    # links: <a href="URL">TEXT</a> -> [TEXT](URL)
    html = re.sub(
        r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>',
        lambda m: f"[{re.sub(r'<.*?>','',m.group(2)).strip()}]({m.group(1)})",
        html,
        flags=re.I | re.S,
    )

    # strip remaining tags (keep images as plain URL if desired)
    html = re.sub(r"<img[^>]+src=\"([^\"]+)\"[^>]*>", r"\n\n![](\1)\n\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", "", html)

    # unescape common entities
    html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    html = re.sub(r"\n{3,}", "\n\n", html).strip()
    return html


def pick_section(feed_url: str, title: str, categories: list[str]) -> str:
    feed_url = (feed_url or "").strip()
    if feed_url in FEED_TO_SECTION:
        return FEED_TO_SECTION[feed_url]

    # 保険
    if "深セン" in title or "深圳" in title:
        return "shenzhen"
    if any(norm_tag(c) == "fabcross" for c in categories):
        return "fabcross"
    return "archive"


def write_hugo_md(out_dir: Path, post_id: str, title: str, date_iso: str, tags: list[str], body_md: str, source_url: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    # filename: <slug>-<id>.md にして衝突回避
    slug = safe_slug(title)[:60]
    filename = f"{slug}-{post_id}.md"
    p = out_dir / filename

    # title escape (ここが f-string で落ちないポイント：事前に作る)
    safe_title = title.replace('"', '\\"')

    tags = [norm_tag(t) for t in tags if norm_tag(t)]
    # dedup
    uniq = []
    for t in tags:
        if t not in uniq:
            uniq.append(t)

    quoted_tags = ", ".join(f'"{t}"' for t in uniq)

    fm = []
    fm.append("---")
    fm.append(f'title: "{safe_title}"')
    if date_iso:
        fm.append(f"date: {date_iso}")
    if uniq:
        fm.append(f"tags: [{quoted_tags}]")
    fm.append(f'source: "{source_url}"')
    fm.append("---")
    fm_text = "\n".join(fm) + "\n\n"

    p.write_text(fm_text + body_md + "\n", encoding="utf-8")
    return p


def main() -> int:
    if not FEEDS_FILE.exists():
        print(f"Missing {FEEDS_FILE}")
        return 1

    TRACK_FILE.touch()
    imported_urls = set(
        normalize_url(ln)
        for ln in TRACK_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        if ln.strip()
    )
    imported_ids = set()
    for u in imported_urls:
        m = re.search(r"/p/([0-9a-f]{6,})$", u)
        if m:
            imported_ids.add(m.group(1))

    feeds = [
        ln.strip()
        for ln in FEEDS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]

    new_count = 0

    for feed in feeds:
        print(f"fetching... {feed}")
        try:
            rss = http_get(feed)
        except Exception as e:
            print("Failed to fetch feed:", feed, e)
            continue

        items = parse_rss(rss)[:40]  # 新着側だけ

        for it in items:
            link = normalize_url(it["link"])
            guid = it["guid"]
            post_id = extract_post_id_from_guid(guid) or ""
            if not post_id:
                continue

            # すでに取り込み済みはスキップ
            if post_id in imported_ids:
                continue

            title = it["title"]
            categories = it["categories"]
            content_html = it["content_html"]
            pub_iso = parse_pubdate_to_iso(it["pubDate"])

            # tags
            tags = [norm_tag(c) for c in categories if c.strip()]
            if (MONTHLY_WORD in title) or any(c in ("月次報告", "monthly-report") for c in categories):
                tags.append(MONTHLY_TAG)

            section = pick_section(feed, title, categories)
            out_dir = SECTION_DIRS.get(section, SECTION_DIRS["archive"])

            body_md = html_to_md(content_html)
            if not body_md:
                # RSSに本文が無いケースは稀だが保険
                body_md = f"[Read on Medium]({link})"

            write_hugo_md(out_dir, post_id, title, pub_iso, tags, body_md, link)

            # 台帳には guid 形式で保存（/p/<id> に寄せる）
            track_url = f"https://medium.com/p/{post_id}"
            with TRACK_FILE.open("a", encoding="utf-8") as f:
                f.write(track_url + "\n")

            imported_ids.add(post_id)
            imported_urls.add(track_url)

            new_count += 1
            time.sleep(0.3)

    print(f"Imported new posts: {new_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
