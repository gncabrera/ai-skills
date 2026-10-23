#!/usr/bin/env python3
"""Pre-commit checks for an Agent Skills repo (see the portable-agent-skills skill).

Usage:
    python3 check_repo.py [REPO] [--denylist PATH]

REPO defaults to the current directory. Exit code 1 if anything FAILs, 0 otherwise
(WARN alone never fails the run), 2 on a usage or missing-repo error.

The denylist holds literal private terms — names, employers, project codenames —
one per line, '#' starts a comment. Keep that file OUTSIDE the repo: a denylist
committed to a public repo is exactly the leak it exists to prevent.
Lookup order: --denylist, $AI_SKILLS_DENYLIST, ~/.config/ai-skills/denylist.txt.

Accepted exceptions go in <REPO>/.skillchecks-ignore, one 'skill:TAG' per line
('*:TAG' for repo-wide), optionally followed by '#' and a reason. Use it for a
deliberate exception such as an upstream skill kept verbatim, never to silence a
finding you have not understood.
"""

import argparse
import os
import re
import sys
from pathlib import Path

DESC_MAX = 1024
BODY_WARN = 20000
ENV_VAR = "AI_SKILLS_DENYLIST"
DEFAULT_DENYLIST = "~/.config/ai-skills/denylist.txt"
IGNORE_NAME = ".skillchecks-ignore"
SCAN_SUFFIXES = (".md", ".json", ".yaml", ".yml", ".txt", ".sh", ".py", ".toml")
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}

# Private regardless of whose name they carry: detect the shape, not the word.
SHAPES = (
    ("PRIVATE_PATH", re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]{2,}/"),
     "absolute home path"),
    ("PRIVATE_EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
     "email address"),
    ("PRIVATE_IP", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                              r"|192\.168\.\d{1,3}\.\d{1,3}"
                              r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"),
     "private IPv4"),
    ("TOKEN", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}"
                         r"|github_pat_[A-Za-z0-9_]{20,}"
                         r"|sk-[A-Za-z0-9]{20,}"
                         r"|xox[baprs]-[A-Za-z0-9-]{10,}"
                         r"|AKIA[0-9A-Z]{16}"
                         r"|glpat-[A-Za-z0-9_-]{20,})\b"),
     "token-shaped string"),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |PGP )?PRIVATE KEY-----"),
     "private key block"),
)
PLACEHOLDER_DOMAINS = ("example.com", "example.org", "example.net", "localhost")
FIX_HINTS = {
    "CRLF": "sed -i 's/\\r$//' <file>   # or add .gitattributes: *.md text eol=lf",
    "DESC_LEN": "trim the description to <= %d chars" % DESC_MAX,
    "NAME": "make the folder name and frontmatter name identical",
    "README_ROW": "add a | [`name`](name/SKILL.md) | ... | row to the README ## Skills table",
    "BODY_SIZE": "move bulk into references/ and point at it",
}

results = []


def add(level, scope, tag, message):
    results.append((level, scope, tag, message))


def load_ignores(repo):
    path = repo / IGNORE_NAME
    ignored = set()
    if not path.is_file():
        return ignored
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            ignored.add(line)
    return ignored


def is_ignored(ignored, scope, tag):
    return (scope + ":" + tag) in ignored or ("*:" + tag) in ignored


def read(path):
    return path.read_text(encoding="utf-8", errors="replace")


def frontmatter(text):
    """Tolerant frontmatter grab: returns the raw block between the first two ---."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return m.group(1) if m else ""


def scalar(fm, key):
    """Read a frontmatter scalar, folding '>-'/'|' continuation lines."""
    m = re.search(r"^" + key + r":[ \t]*(.*)$", fm, re.M)
    if not m:
        return None
    value = m.group(1).strip()
    if value in (">-", ">", "|", "|-"):
        lines = fm[m.end():].splitlines()
        parts = []
        for line in lines:
            if line.strip() and not line.startswith((" ", "\t")):
                break
            parts.append(line.strip())
        value = " ".join(part for part in parts if part)
    return value.strip().strip("'\"")


def markdown_files(repo):
    for path in sorted(repo.rglob("*.md")):
        if not any(part in SKIP_DIRS for part in path.parts):
            yield path


def check_skills(repo, ignored):
    readme_path = repo / "README.md"
    if not readme_path.is_file():
        add("FAIL", "*", "README", "README.md is missing — the table is the only index")
        table = set()
    else:
        table = set(re.findall(r"^\|\s*\[`([^`]+)`\]", read(readme_path), re.M))

    folders = sorted(p.parent.name for p in repo.glob("*/SKILL.md"))
    if not folders:
        add("FAIL", "*", "LAYOUT", "no <skill>/SKILL.md found under %s" % repo)

    for folder in folders:
        def flag(level, tag, message, _folder=folder):
            if not is_ignored(ignored, _folder, tag):
                add(level, _folder, tag, message)

        path = repo / folder / "SKILL.md"
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        fm = frontmatter(text)
        if not fm:
            flag("FAIL", "FRONTMATTER", "%s/SKILL.md has no frontmatter block" % folder)
        name = scalar(fm, "name") if fm else None
        if name != folder:
            flag("FAIL", "NAME", "folder=%s frontmatter name=%s" % (folder, name or "MISSING"))
        desc = scalar(fm, "description") if fm else None
        if not desc:
            flag("FAIL", "DESC", "no description")
        elif len(desc) > DESC_MAX:
            flag("FAIL", "DESC_LEN",
                 "description is %d chars (> %d) — clients may truncate it" % (len(desc), DESC_MAX))
        if b"\r" in raw:
            flag("FAIL", "CRLF", "%s/SKILL.md has CRLF line endings" % folder)
        if folder not in table:
            flag("FAIL", "README_ROW", "%s is not in the README ## Skills table" % folder)
        if len(text) > BODY_WARN:
            flag("WARN", "BODY_SIZE",
                 "%s/SKILL.md is %d chars — consider splitting into references/" % (folder, len(text)))


def strip_code(text):
    """Drop fenced blocks and inline spans before looking for links: a link inside
    an example fence is illustrative, not navigational. Privacy scanning keeps
    them — a real path hides in a command example far more often than in prose."""
    text = re.sub(r"(?ms)^[ \t]*(?:```|~~~).*?^[ \t]*(?:```|~~~)[ \t]*$", "", text)
    return re.sub(r"`[^`\n]*`", "", text)


def check_links(repo, ignored):
    """Relative markdown links, resolved against the containing file. Catches a
    stale link after a folder rename; it cannot catch a stale prose mention."""
    pattern = re.compile(r"\]\(([^)]+)\)")
    for md in markdown_files(repo):
        scope = md.parent.name if md.parent != repo else "*"
        if md.name == "SKILL.md":
            scope = md.parent.name
        if is_ignored(ignored, scope, "LINK"):
            continue
        for target in pattern.findall(strip_code(read(md))):
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0].strip()
            if not target:
                continue
            if not (md.parent / target).exists() and not (repo / target).exists():
                add("FAIL", scope, "LINK",
                    "%s -> %s does not resolve" % (md.relative_to(repo), target))


def private_patterns(denylist_path):
    patterns = list(SHAPES)
    if denylist_path and denylist_path.is_file():
        words = [w.split("#", 1)[0].strip() for w in read(denylist_path).splitlines()]
        words = [w for w in words if w]
        if words:
            joined = "|".join(re.escape(w) for w in words)
            patterns.append(("DENYLIST", re.compile(joined, re.I), "denylisted private term"))
    return patterns


def check_private(repo, ignored, patterns):
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(repo)
        scope = rel.parts[0] if len(rel.parts) > 1 else "*"
        for line_no, line in enumerate(read(path).splitlines(), 1):
            for tag, regex, label in patterns:
                if is_ignored(ignored, scope, tag):
                    continue
                hit = regex.search(line)
                if not hit:
                    continue
                if tag == "PRIVATE_EMAIL":
                    domain = hit.group(0).split("@", 1)[-1].lower()
                    if domain in PLACEHOLDER_DOMAINS:
                        continue
                add("FAIL", scope, tag,
                    "%s:%d  %s -> %s" % (rel, line_no, label, hit.group(0)[:60]))


def report():
    order = {"FAIL": 0, "WARN": 1}
    results.sort(key=lambda r: (order.get(r[0], 9), r[1], r[3]))
    for level, scope, tag, message in results:
        print("%-4s %-14s %-12s %s" % (level, scope, tag, message))
        if level == "FAIL" and tag in FIX_HINTS:
            print("     %-14s fix: %s" % ("", FIX_HINTS[tag]))
    fails = sum(1 for r in results if r[0] == "FAIL")
    warns = sum(1 for r in results if r[0] == "WARN")
    print("\n%d FAIL  %d WARN" % (fails, warns))
    return 1 if fails else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pre-commit checks for an Agent Skills repo.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--denylist", default=None,
                        help="literal private terms, one per line (keep it OUTSIDE the repo)")
    args = parser.parse_args(argv)

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print("error: %s is not a directory" % repo, file=sys.stderr)
        return 2

    denylist = args.denylist or os.environ.get(ENV_VAR) or DEFAULT_DENYLIST
    ignored = load_ignores(repo)
    if ignored:
        print("(ignoring %d exception(s) from %s)\n" % (len(ignored), IGNORE_NAME))

    check_skills(repo, ignored)
    check_links(repo, ignored)
    check_private(repo, ignored, private_patterns(Path(denylist).expanduser()))
    return report()


if __name__ == "__main__":
    sys.exit(main())
