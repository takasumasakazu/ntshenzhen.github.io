#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FEEDS_FILE = ROOT / "tools" / "medium_feeds.txt"
TRACK_FILE = ROOT / "medium_imported_urls.txt"

# Hugo セクション（保存先）
SECTION_DIRS = {
    "teardown": ROOT / "content" / "teardown",
    "shenzhen": ROOT / "content" / "shenzhen",
    "fabcross": ROOT / "content" / "fabcross",
    "archive": ROOT / "content" / "archive",
}

# Publication slug → セクション（あなたの5つを固定で判定）
PUB_TO_SECTION = {
    "bunkai": "teardown",
    "%E5%88%86%E8%A7%A3%E3%81%AE%E3%82%B9%E3%82%B9%E3%83%A1": "teardown",  # 「分解のススメ」(URLエンコード版)
    "shenzhen-high-tour-by-makers": "shenzhen",
    "fabcross%E9%81%8E%E5%8E%BB%E9%80%A3%E8%BC%89": "fabcross",
    "%E3%83%96%E3%83%AD%E3%83%9E%E3%82%AC%E9%81%8E%E5%8E%BB%E8%A8%98%E4%BA%8B%E3%82%B5%E3%83%AB%E3%83%99%E3%83%BC%E3%82%B8": "archive",
    "ecosystembymakers": "archive",  # ここを "fabcross" に寄せたいなら変更OK
}

# タイトル/タグのキーワードで判定（保険）
KEYWORDS_TO_SECTION = [
    ({"teardown", "reverse-engineering", "decap", "chip", "分解", "デカップ"}, "teardown"),
    ({"shenzhen", "深セン", "深圳"}, "shenzhen"),
    ({"fabcross"}, "fabcross"),
]

MONTHLY_WORD = "月次報告"
MONTHLY_TAG = "monthly-report"

UA = "Mozilla/5.0 (compatible; MediumImporter/1.1)"


# --------------------------
# URL / ID / tag utilities
# --------------------------

def normalize_url(url: str) -> str:
    url = url.strip()
    if url.startswith("ttps://"):
        url = "h" + url
    # strip query & fragment
    url = url.split("?")[0].split("#")[0]
    # strip trailing punctuation / html-ish leftovers
    url = re.sub(r'[<>"\')\],].*$', "", url).strip()
    # normalize trailing slash (keep /p/<id>/ as /p/<id>)
    if re.match(r"^https://medium\.com/p/[0-9a-f]{6,}/?$", url):
        url = url.rstrip("/")
    return url


def extract_post_id(url: str) -> str | None:
    """
    Mediumの同一記事を同定するID（末尾のhex）をURLから抽出。
    例:
      https://medium.com/p/84ef3ed1da2
      https://medium.com/shenzhen-high-tour-by-makers/...-84ef3ed1da2
      https://tks.medium.com/...-84ef3ed1da2
    """
    u = normalize_url(url)

    m = re.search(r"^https://medium\.com/p/([0-9a-f]{6,})$", u)
    if m:
        return m.group(1)

    m = re.search(r"-([0-9a-f]{8,})$", u)
    if m:
        return m.group(1)

    return None


def norm_tag(t: str) -> str:
    t = t.strip().lower()
    t = re.sub(r"\s+", "-", t)
    # allow JP/CN, but normalize separators
    t = re.sub(r"[^a-z0-9\-\u3040-\u30ff\u4e00-\u9fff]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t


# --------------------------
# Fetch / RSS parsing
# --------------------------

def fetch(url: str, timeout=30) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_rss_links(xml_text: str) -> list[str]:
    links: list[str] = []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return links

    for item in root.findall(".//item"):
        link_el = item.find("link")
        if link_el is None or not link_el.text:
            continue
        u = normalize_url(link_el.text)
        if u and u not in links:
            links.append(u)
    return links


# --------------------------
# Classification
# --------------------------

def url_publication_slug(url: str) -> str | None:
    """
    https://medium.com/<slug>/...  の <slug> を返す
    """
    u = normalize_url(url)
    m = re.match(r"^https://medium\.com/([^/]+)/", u)
    if not m:
        return None
    return m.group(1)


def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()


def extract_tags_from_html(html: str) -> list[str]:
    tags: list[str] = []

    # 1) <meta property="article:tag" content="...">
    for m in re.finditer(
        r'<meta\s+property=["\']article:tag["\']\s+content=["\']([^"\']+)["\']',
        html, re.I
    ):
        tags.append(m.group(1))

    # 2) JSON-LD keywords
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S
    ):
        blob = m.group(1).strip()
        try:
            data = json.loads(blob)
            if isinstance(data, dict):
                kw = data.get("keywords")
                if isinstance(kw, str):
                    tags.extend([x.strip() for x in kw.split(",") if x.strip()])
                elif isinstance(kw, list):
                    tags.extend([str(x) for x in kw if str(x).strip()])
        except Exception:
            pass

    tags = [norm_tag(t) for t in tags if t and t.strip()]
    out: list[str] = []
    for t in tags:
        if t and t not in out:
            out.append(t)
    return out


def pick_section(url: str, tags: list[str], title: str) -> str:
    # 1) publication slug で確定（最強）
    slug = url_publication_slug(url)
    if slug and slug in PUB_TO_SECTION:
        return PUB_TO_SECTION[slug]

    # 2) tag/タイトルで判定（保険）
    tagset = set(tags)
    for keys, sec in KEYWORDS_TO_SECTION:
        keys_norm = {norm_tag(k) for k in keys}
        if tagset.intersection(keys_norm):
            return sec
        if any(k in title for k in keys):
            return sec

    # 3) 最後の救済
    if "深セン" in title or "深圳" in title:
        return "shenzhen"

    return "archive"


# --------------------------
# Hugo writing helpers
# --------------------------

def run_mediumexporter(url: str, out_dir: Path) -> bool:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["npx", "--yes", "mediumexporter", url, "--frontmatter", "--hugo", "-O", str(out_dir)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print("mediumexporter failed:", url)
        print(e.stderr[-1200:])
        return False


def add_tags_to_latest_md(out_dir: Path, tags: list[str], is_monthly: bool) -> None:
    """
    mediumexporter が吐いた最新 .md の frontmatter に tags を注入/置換する。
    YAML (---) と TOML (+++) の両対応。
    """
    mds = sorted(out_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mds:
        return

    p = mds[0]
    text = p.read_text(encoding="utf-8", errors="replace")

    # merge tags (dedup)
    merged: list[str] = []
    for t in tags + ([MONTHLY_TAG] if is_monthly else []):
        t = norm_tag(t)
        if t and t not in merged:
            merged.append(t)

    if not merged:
        return

    # f-string の式中にバックスラッシュを含めないように、先に作る
    quoted = ", ".join(f'"{t}"' for t in merged)

    if text.startswith("---"):
        # YAML frontmatter
        # 既存 tags を削除（配列1行形式 / リスト形式 両対応）
        text = re.sub(r'^\s*tags\s*:\s*\[(.*?)\]\s*$\n?', "", text, flags=re.M)
        text = re.sub(r'^\s*tags\s*:\s*\n((?:\s*-\s*.+\n)+)', "", text, flags=re.M)

        tags_line = f"tags: [{quoted}]\n"

        # title行の直後に挿入（titleが無い場合は --- の直後に挿入）
        if re.search(r'^\s*title\s*:\s*.+$', text, re.M):
            text = re.sub(
                r'^(\s*title\s*:\s*.+\n)',
                lambda m: m.group(1) + tags_line,
                text,
                flags=re.M
            )
        else:
            text = re.sub(
                r'^(---\s*\n)',
                lambda m: m.group(1) + tags_line,
                text,
                flags=re.M
            )

    elif text.startswith("+++"):
        # TOML frontmatter
        tags_line = f"tags = [{quoted}]\n"

        if re.search(r'^\s*tags\s*=', text, re.M):
            text = re.sub(
                r'^\s*tags\s*=\s*\[(.*?)\]\s*$',
                f"tags = [{quoted}]",
                text,
                flags=re.M
            )
        else:
            if re.search(r'^\s*title\s*=\s*.+$', text, re.M):
                text = re.sub(
                    r'^(\s*title\s*=\s*.+\n)',
                    lambda m: m.group(1) + tags_line,
                    text,
                    flags=re.M
                )
            else:
                text = re.sub(
                    r'^(\+\+\+\s*\n)',
                    lambda m: m.group(1) + tags_line,
                    text,
                    flags=re.M
                )

    p.write_text(text, encoding="utf-8")


# --------------------------
# Main
# --------------------------

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
        pid = extract_post_id(u)
        if pid:
            imported_ids.add(pid)

    feeds = [
        ln.strip()
        for ln in FEEDS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]

    new_count = 0

    for feed in feeds:
        try:
            rss = fetch(feed)
        except Exception as e:
            print("Failed to fetch feed:", feed, e)
            continue

        urls = parse_rss_links(rss)[:200]  # 新着側だけ
        for url in urls:
            url = normalize_url(url)
            if not url:
                continue

pid = extract_post_id(url)

if pid and pid in imported_ids:
    # print(f"[skip] already imported id={pid} url={url}")
    continue
if url in imported_urls:
    # print(f"[skip] already imported url={url}")
    continue

            try:
                html = fetch(url)
            except Exception as e:
                print("Failed to fetch post:", url, e)
                continue

print(f"[feed] {feed}")
print(f"[feed] items={len(parse_rss_links(rss))} (showing up to 5)")
for u in parse_rss_links(rss)[:5]:
    print("  -", normalize_url(u))


            title = extract_title(html)
            tags = extract_tags_from_html(html)
            section = pick_section(url, tags, title)
            out_dir = SECTION_DIRS.get(section, SECTION_DIRS["archive"])

            ok = run_mediumexporter(url, out_dir)
            if ok:
                add_tags_to_latest_md(out_dir, tags, (MONTHLY_WORD in title))

                with TRACK_FILE.open("a", encoding="utf-8") as f:
                    f.write(url + "\n")

                imported_urls.add(url)
                if pid:
                    imported_ids.add(pid)

                new_count += 1

            time.sleep(1.0)

    print(f"Imported new posts: {new_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
