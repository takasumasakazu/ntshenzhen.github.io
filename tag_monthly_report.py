#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import argparse
import os
import re
from pathlib import Path
from typing import Optional, Tuple, List

TARGET_TAG = "monthly-report"
MATCH_WORD = "月次報告"

def split_frontmatter(text: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Returns (fm_type, fm_body, rest)
    fm_type: 'yaml' or 'toml' or None
    """
    if text.startswith("---\n") or text.startswith("---\r\n"):
        # YAML
        m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", text, re.S)
        if not m:
            return None, None, text
        return "yaml", m.group(1), m.group(2)
    if text.startswith("+++\n") or text.startswith("+++\r\n"):
        # TOML
        m = re.match(r"^\+\+\+\s*\r?\n(.*?)\r?\n\+\+\+\s*\r?\n(.*)$", text, re.S)
        if not m:
            return None, None, text
        return "toml", m.group(1), m.group(2)
    return None, None, text

def get_title(fm_type: str, fm_body: str) -> Optional[str]:
    if fm_type == "yaml":
        # title: "..."
        m = re.search(r'^\s*title\s*:\s*(.+?)\s*$', fm_body, re.M)
        if not m:
            return None
        raw = m.group(1).strip()
        return strip_quotes(raw)
    if fm_type == "toml":
        # title = "..."
        m = re.search(r'^\s*title\s*=\s*(.+?)\s*$', fm_body, re.M)
        if not m:
            return None
        raw = m.group(1).strip()
        return strip_quotes(raw)
    return None

def strip_quotes(s: str) -> str:
    s = s.strip()
    # remove trailing comments for TOML like "title" # comment
    s = re.split(r"\s+#", s, maxsplit=1)[0].strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def ensure_tag_in_yaml(fm_body: str, tag: str) -> Tuple[str, bool]:
    """
    Add tag to YAML frontmatter. Returns (new_body, changed)
    Supports:
      tags: ["a","b"]
      tags: [a, b]
      tags:
        - a
        - b
      tags: a
    """
    changed = False

    # Case 1: tags: [ ... ]
    m = re.search(r'^\s*tags\s*:\s*\[(.*?)\]\s*$', fm_body, re.M)
    if m:
        inner = m.group(1).strip()
        items = [strip_quotes(x.strip()) for x in inner.split(",") if x.strip()]
        if tag not in items:
            items.append(tag)
            new_inner = ", ".join([f'"{x}"' for x in items])
            fm_body = re.sub(r'^\s*tags\s*:\s*\[(.*?)\]\s*$',
                             f'tags: [{new_inner}]',
                             fm_body, flags=re.M)
            changed = True
        return fm_body, changed

    # Case 2: tags: single
    m = re.search(r'^\s*tags\s*:\s*(.+?)\s*$', fm_body, re.M)
    if m:
        # Could be block list too; handle block list separately below
        line = m.group(0)
        val = m.group(1).strip()
        if val == "" or val in ("|", ">"):
            # ignore weird YAML scalars
            pass
        else:
            # If it's already "tags:" with next lines as - items, we'll handle later
            # Detect if this is "tags:" alone
            if re.match(r'^\s*tags\s*:\s*$', line):
                pass
            else:
                items = [strip_quotes(val)]
                if tag not in items:
                    items.append(tag)
                    new_line = f'tags: ["{items[0]}", "{items[1]}"]' if len(items) == 2 else f'tags: {items}'
                    fm_body = re.sub(r'^\s*tags\s*:\s*(.+?)\s*$',
                                     f'tags: ["{items[0]}", "{items[1]}"]',
                                     fm_body, flags=re.M)
                    changed = True
                return fm_body, changed

    # Case 3: block list:
    # tags:
    #   - a
    #   - b
    m = re.search(r'^\s*tags\s*:\s*\r?\n((?:\s*-\s*.+\r?\n)+)', fm_body, re.M)
    if m:
        block = m.group(1)
        items = [strip_quotes(re.sub(r'^\s*-\s*', '', ln).strip())
                 for ln in block.splitlines() if ln.strip().startswith("-")]
        if tag not in items:
            # Append another "- tag"
            insert = block + f"  - {tag}\n"
            fm_body = fm_body[:m.start(1)] + insert + fm_body[m.end(1):]
            changed = True
        return fm_body, changed

    # Case 4: no tags field at all → insert near title if possible, else at end
    if re.search(r'^\s*title\s*:\s*', fm_body, re.M):
        fm_body = re.sub(r'^(\s*title\s*:\s*.+\s*)$',
                         r'\1\n' + f'tags: ["{tag}"]',
                         fm_body, flags=re.M)
    else:
        fm_body = fm_body.rstrip() + "\n" + f'tags: ["{tag}"]' + "\n"
    changed = True
    return fm_body, changed

def ensure_tag_in_toml(fm_body: str, tag: str) -> Tuple[str, bool]:
    """
    Add tag to TOML frontmatter.
    Supports:
      tags = ["a","b"]
      tags = "a" (rare)
    """
    changed = False

    m = re.search(r'^\s*tags\s*=\s*\[(.*?)\]\s*$', fm_body, re.M)
    if m:
        inner = m.group(1).strip()
        items = [strip_quotes(x.strip()) for x in inner.split(",") if x.strip()]
        if tag not in items:
            items.append(tag)
            new_inner = ", ".join([f'"{x}"' for x in items])
            fm_body = re.sub(r'^\s*tags\s*=\s*\[(.*?)\]\s*$',
                             f'tags = [{new_inner}]',
                             fm_body, flags=re.M)
            changed = True
        return fm_body, changed

    m = re.search(r'^\s*tags\s*=\s*(.+?)\s*$', fm_body, re.M)
    if m:
        val = strip_quotes(m.group(1).strip())
        if val != tag:
            fm_body = re.sub(r'^\s*tags\s*=\s*(.+?)\s*$',
                             f'tags = ["{val}", "{tag}"]',
                             fm_body, flags=re.M)
            changed = True
        return fm_body, changed

    # no tags → insert after title if possible
    if re.search(r'^\s*title\s*=\s*', fm_body, re.M):
        fm_body = re.sub(r'^(\s*title\s*=\s*.+\s*)$',
                         r'\1\n' + f'tags = ["{tag}"]',
                         fm_body, flags=re.M)
    else:
        fm_body = fm_body.rstrip() + "\n" + f'tags = ["{tag}"]' + "\n"
    changed = True
    return fm_body, changed

def process_file(path: Path, apply: bool) -> Tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    fm_type, fm_body, rest = split_frontmatter(text)
    if not fm_type or fm_body is None:
        return False, "skip(no frontmatter)"

    title = get_title(fm_type, fm_body) or ""
    if MATCH_WORD not in title:
        return False, "skip(no match)"

    if fm_type == "yaml":
        new_body, changed = ensure_tag_in_yaml(fm_body, TARGET_TAG)
        fence = "---"
    else:
        new_body, changed = ensure_tag_in_toml(fm_body, TARGET_TAG)
        fence = "+++"

    if not changed:
        return False, "ok(already tagged)"

    new_text = f"{fence}\n{new_body.rstrip()}\n{fence}\n{rest}"
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return True, "changed"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Actually write changes")
    ap.add_argument("--root", default="content", help="Root content dir (default: content)")
    args = ap.parse_args()

    root = Path(args.root)
    md_files = list(root.rglob("*.md"))

    changed_files: List[Path] = []
    for p in md_files:
        changed, msg = process_file(p, apply=args.apply)
        if changed:
            changed_files.append(p)
        # Print only relevant hits
        if "skip(no match)" not in msg and "skip(no frontmatter)" not in msg:
            print(f"{msg:18} {p}")

    print("\n---")
    print(f"Matched files changed: {len(changed_files)}")
    if not args.apply:
        print("Dry-run only. Re-run with --apply to write changes.")

if __name__ == "__main__":
    main()
