#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
FEEDS_FILE = ROOT / "tools" / "medium_feeds.txt"
TRACK_FILE = ROOT / "medium_imported_urls.txt"
LOCK_FILE = ROOT / "tools" / ".import_medium.lock"

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

UA = "Mozilla/5.0 (compatible; MediumImporter/2.1)"

# Optional: mediumexporter をどうしても使いたい場合だけ指定
# 例:
#   export MEDIUMEXPORTER_CMD='mediumexporter "{url}"'
#   export MEDIUMEXPORTER_CMD='node tools/mediumexporter.mjs "{url}"'
MEDIUMEXPORTER_CMD = os.environ.get("MEDIUMEXPORTER_CMD", "").strip()

# fetch tuning
SLEEP_MIN = float(os.environ.get("MEDIUM_IMPORT_SLEEP_MIN", "0.2"))
SLEEP_MAX = float(os.environ.get("MEDIUM_IMPORT_SLEEP_MAX", "0.8"))
HTTP_MAX_RETRIES = int(os.environ.get("MEDIUM_HTTP_MAX_RETRIES", "5"))
HTTP_TIMEOUT = int(os.environ.get("MEDIUM_HTTP_TIMEOUT", "30"))


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("ttps://"):
        url = "h" + url
    url = url.split("?")[0].split("#")[0].strip()
    return url.rstrip("/")


def acquire_lock() -> None:
    if LOCK_FILE.exists():
        raise SystemExit(f"Lock exists: {LOCK_FILE} (another import running?)")
    LOCK_FILE.write_text(datetime.now().isoformat(), encoding="utf-8")


def release_lock() -> None:
    try:
        LOCK_FILE.unlink()
    except FileNotFoundError:
        pass


def sleep_jitter() -> None:
    time.sleep(SLEEP_MIN + random.random() * max(0.0, (SLEEP_MAX - SLEEP_MIN)))


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


def http_get(url: str, timeout: int = HTTP_TIMEOUT, max_retries: int = HTTP_MAX_RETRIES) -> str:
    """
    Cloudflare系の 429/503 で落ちにくい http_get（軽いバックオフ＋ジッター）
    """
    import urllib.request

    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en;q=0.8",
        "Connection": "close",
    }

    last_err: Exception | None = None

    for i in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")

        except HTTPError as e:
            last_err = e
            code = getattr(e, "code", None)
            if code in (429, 502, 503):
                # exponential backoff + jitter
                sleep_s = min(60.0, (2 ** i) + random.random())
                time.sleep(sleep_s)
                continue
            raise

        except URLError as e:
            last_err = e
            sleep_s = min(30.0, (2 ** i) + random.random())
            time.sleep(sleep_s)
            continue

    raise RuntimeError(f"http_get failed after retries: {url} ({last_err})")


def parse_pubdate_to_iso(pubdate: str) -> str:
    # example: Tue, 10 Feb 2026 05:28:47 GMT
    try:
        dt = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return ""


def rss_content_looks_truncated(title: str, html: str) -> bool:
    """
    RSS本文が短すぎる/途中で切れている疑いがあるか（長文・画像多い記事対策の入口）
    """
    h = (html or "").strip().lower()
    if not h:
        return True
    if "continue reading" in h or "read more" in h:
        return True

    # remove tags and check length
    text_only = re.sub(r"<[^>]+>", "", html)
    if len(text_only.strip()) < 800:
        return True
    return False


def strip_medium_json_prefix(s: str) -> str:
    """
    Mediumの ?format=json に付くことがある anti-JSON-hijacking prefix を剥がす
    """
    if not s:
        return s
    i = s.find("{")
    return s[i:] if i >= 0 else s


def apply_markups(text: str, markups: list[dict]) -> str:
    """
    Medium bodyModel の markups をざっくり Markdown に寄せる（太字/斜体/リンク）
    - 正確なレンダリングを狙うと大変なので、最低限の実用ラインに寄せる
    """
    if not text or not markups:
        return text

    # markups: [{"type": ..., "start": ..., "end": ..., "href": ...}, ...]
    # 末尾から適用（インデックス崩れ防止）
    def wrap(s: str, mk: dict) -> str:
        t = mk.get("type")
        href = mk.get("href")
        if t == 1:  # bold
            return f"**{s}**"
        if t == 2:  # italic
            return f"*{s}*"
        if t == 3 and href:  # link
            return f"[{s}]({href})"
        # その他は素通し
        return s

    # sort by start desc
    markups_sorted = sorted(
        [m for m in markups if isinstance(m, dict) and "start" in m and "end" in m],
        key=lambda m: (int(m.get("start", 0)), int(m.get("end", 0))),
        reverse=True,
    )

    out = text
    for mk in markups_sorted:
        try:
            a = int(mk.get("start", 0))
            b = int(mk.get("end", 0))
            if 0 <= a <= b <= len(out):
                seg = out[a:b]
                out = out[:a] + wrap(seg, mk) + out[b:]
        except Exception:
            continue
    return out


def medium_json_to_md(data: dict) -> str:
    """
    Medium ?format=json の payload/value/content/bodyModel/paragraphs から Markdown を生成
    """
    payload = data.get("payload") or {}
    value = payload.get("value") or {}
    content = value.get("content") or {}
    body = content.get("bodyModel") or {}
    paragraphs = body.get("paragraphs") or []

    lines: list[str] = []

    for p in paragraphs:
        if not isinstance(p, dict):
            continue

        ptype = p.get("type")
        text = (p.get("text") or "").rstrip()

        # image paragraph
        # 多くのケースで metadata.id が imageId
        meta = p.get("metadata") or {}
        image_id = meta.get("id") or meta.get("originalWidth")  # originalWidth は念のため（通常idがある）

        # Medium paragraph type heuristic:
        # 1: text
        # 2/3: heading-ish (varies)
        # 8: code (often)
        if ptype in (8,):
            if text.strip():
                lines.append("```")
                lines.append(text)
                lines.append("```")
                lines.append("")
            continue

        # headings (heuristic)
        if ptype in (2, 3) and text.strip():
            # ptype=2 を H2, ptype=3 を H3 くらいに寄せる
            prefix = "## " if ptype == 2 else "### "
            lines.append(prefix + apply_markups(text, p.get("markups") or []))
            lines.append("")
            continue

        # image heuristic: if type indicates image or has metadata.id and no text
        if (ptype in (4, 10, 11) or (meta.get("id") and not text.strip())) and meta.get("id"):
            img_id = meta.get("id")
            # v2 で安定しやすいURL（hotlinkのまま）。本番でローカル保存までやるなら別途実装。
            img_url = f"https://miro.medium.com/v2/resize:fit:1400/{img_id}"
            lines.append(f"![]({img_url})")
            lines.append("")
            continue

        # normal text
        if text.strip():
            lines.append(apply_markups(text, p.get("markups") or []))
            lines.append("")

    md = "\n".join(lines).strip()
    return md


def fetch_medium_full_md(url: str) -> str:
    """
    RSSが欠けてそうな時に、より確実に全文を取る。
    優先順位:
      1) ?format=json から bodyModel -> md
      2) MEDIUMEXPORTER_CMD が指定されていればそれで md 取得
      3) 取れなければ空文字
    """
    # 1) format=json
    try:
        json_text = http_get(url + "?format=json")
        json_text = strip_medium_json_prefix(json_text)
        data = json.loads(json_text)
        md = medium_json_to_md(data)
        if md:
            return md
    except Exception:
        pass

    # 2) mediumexporter (optional)
    if MEDIUMEXPORTER_CMD:
        try:
            cmd = MEDIUMEXPORTER_CMD.format(url=url)
            p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            if p.returncode == 0 and (p.stdout or "").strip():
                return p.stdout.strip()
        except Exception:
            pass

    return ""


def html_to_md(html: str) -> str:
    """
    超ざっくり変換（RSS本文はHTMLなので、まずは最低限でOK）
    """
    if not html:
        return ""

    # remove Medium tracking image
    html = re.sub(r'<img[^>]+medium\.com/_/stat[^>]*>', "", html, flags=re.I)
    # remove "Originally published in..." block (雑)
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

    # images:
    # 1) src がある場合
    html = re.sub(r"<img[^>]+src=\"([^\"]+)\"[^>]*>", r"\n\n![](\1)\n\n", html, flags=re.I)
    # 2) src が無いが srcset がある場合（先頭URLを拾う）
    def _img_srcset_to_md(m):
        srcset = m.group(1) or ""
        first = srcset.split(",")[0].strip().split(" ")[0].strip()
        return f"\n\n![]({first})\n\n" if first else "\n\n"
    html = re.sub(r"<img[^>]+srcset=\"([^\"]+)\"[^>]*>", _img_srcset_to_md, html, flags=re.I)

    # strip remaining tags
    html = re.sub(r"<[^>]+>", "", html)

    # unescape common entities
    html = (
        html.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
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


def write_hugo_md(
    out_dir: Path,
    post_id: str,
    title: str,
    date_iso: str,
    tags: list[str],
    body_md: str,
    source_url: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    # filename: <slug>-<id>.md にして衝突回避
    slug = safe_slug(title)[:60]
    filename = f"{slug}-{post_id}.md"
    p = out_dir / filename

    safe_title = title.replace('"', '\\"')

    tags = [norm_tag(t) for t in tags if norm_tag(t)]
    # dedup
    uniq: list[str] = []
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

    acquire_lock()
    try:
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
        fallback_count = 0
        feed_fail = 0

        for feed in feeds:
            print(f"fetching... {feed}")
            try:
                rss = http_get(feed)
            except Exception as e:
                print("Failed to fetch feed:", feed, e)
                feed_fail += 1
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

                # まずRSSで変換
                body_md = html_to_md(content_html)

                # 長文/画像多い記事でRSSが欠けやすい → フォールバックで全文取得
                if not body_md or rss_content_looks_truncated(title, content_html):
                    md_full = fetch_medium_full_md(link)
                    if md_full:
                        body_md = md_full
                        fallback_count += 1

                if not body_md:
                    # 最後の保険
                    body_md = f"[Read on Medium]({link})"

                write_hugo_md(out_dir, post_id, title, pub_iso, tags, body_md, link)

                # 台帳には guid 形式で保存（/p/<id> に寄せる）
                track_url = f"https://medium.com/p/{post_id}"
                with TRACK_FILE.open("a", encoding="utf-8") as f:
                    f.write(track_url + "\n")

                imported_ids.add(post_id)
                imported_urls.add(track_url)

                new_count += 1
                sleep_jitter()

        print(f"Imported new posts: {new_count} (fulltext fallback used: {fallback_count}, feed failures: {feed_fail})")
        return 0

    finally:
        release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
