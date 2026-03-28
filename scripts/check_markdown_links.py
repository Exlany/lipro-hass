"""Check local Markdown links for the public/docs-first route surfaces.

Usage:
    uv run python scripts/check_markdown_links.py
"""
# ruff: noqa: T201

from __future__ import annotations

from collections import Counter
from functools import cache
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

_ROOT = Path(__file__).resolve().parent.parent
_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(?P<title>.+?)\s*$", re.MULTILINE)
_IGNORED_SCHEMES = {"http", "https", "mailto", "tel", "data"}
_ROOT_MARKDOWN_FILES = (
    'README.md',
    'README_zh.md',
    'CONTRIBUTING.md',
    'SUPPORT.md',
    'SECURITY.md',
    'CHANGELOG.md',
    'CODE_OF_CONDUCT.md',
    '.github/pull_request_template.md',
)


def _iter_markdown_files() -> list[Path]:
    files = [(_ROOT / relative_path) for relative_path in _ROOT_MARKDOWN_FILES]
    files.extend(sorted((_ROOT / 'docs').rglob('*.md')))
    return [path for path in files if path.exists()]


def _normalize_destination(raw_destination: str) -> str:
    destination = raw_destination.strip()
    if destination.startswith('<') and destination.endswith('>'):
        destination = destination[1:-1].strip()
    for separator in (' "', " '", ' ('):
        if separator in destination:
            destination = destination.split(separator, 1)[0].strip()
    return destination


def _is_external(destination: str) -> bool:
    parsed = urlparse(destination)
    return parsed.scheme in _IGNORED_SCHEMES


def _slugify(title: str) -> str:
    lowered = title.strip().lower().replace('`', '')
    lowered = re.sub(r"[^\w一-鿿\- ]", '', lowered)
    lowered = re.sub(r"\s+", '-', lowered)
    lowered = re.sub(r"-+", '-', lowered)
    return lowered.strip('-')


@cache
def _heading_index(path: Path) -> set[str]:
    headings = []
    for match in _HEADING_RE.finditer(path.read_text(encoding='utf-8')):
        slug = _slugify(match.group('title'))
        if slug:
            headings.append(slug)
    counts: Counter[str] = Counter()
    anchors: set[str] = set()
    for heading in headings:
        counts[heading] += 1
        if counts[heading] == 1:
            anchors.add(heading)
        else:
            anchors.add(f"{heading}-{counts[heading] - 1}")
    return anchors


def _resolve_target(source: Path, destination: str) -> tuple[Path, str | None]:
    path_part, has_fragment, fragment = destination.partition('#')
    target = source if not path_part else (source.parent / unquote(path_part)).resolve()
    return target, unquote(fragment) if has_fragment else None


def main() -> int:
    """Run the Markdown local-link checker for docs-first surfaces."""
    errors: list[str] = []
    checked = 0

    for source in _iter_markdown_files():
        text = source.read_text(encoding='utf-8')
        for raw_destination in _LINK_RE.findall(text):
            destination = _normalize_destination(raw_destination)
            if not destination or _is_external(destination):
                continue
            target, fragment = _resolve_target(source, destination)
            checked += 1
            if not target.exists():
                errors.append(
                    f"{source.relative_to(_ROOT).as_posix()}: missing target for {destination!r} -> {target.relative_to(_ROOT).as_posix()}"
                )
                continue
            if fragment and target.suffix.lower() == '.md':
                anchors = _heading_index(target)
                if fragment not in anchors:
                    errors.append(
                        f"{source.relative_to(_ROOT).as_posix()}: missing anchor #{fragment} in {target.relative_to(_ROOT).as_posix()}"
                    )

    if errors:
        print('❌ Markdown link check failed:')
        for error in errors:
            print(f'  - {error}')
        return 1

    print(f'✅ Markdown link check passed! ({checked} local links checked)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
