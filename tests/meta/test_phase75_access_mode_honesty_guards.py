"""Focused guards for Phase 75 private-access honesty."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib
from typing import cast

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PYPROJECT = _ROOT / "pyproject.toml"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
_BUG_TEMPLATE = _ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml"
_DOCS_README = _ROOT / "docs" / "README.md"


def _load_yaml(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def test_private_access_metadata_avoids_public_interactive_routes() -> None:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    urls = pyproject["project"]["urls"]
    release_ref = f"/blob/v{pyproject['project']['version']}/"

    assert urls["Documentation"].endswith("/docs/README.md")
    assert urls["Support"].endswith("/SUPPORT.md")
    assert urls["Security"].endswith("/SECURITY.md")
    assert "Discussions" not in urls
    assert "Issues" not in urls
    assert manifest["documentation"].endswith("/docs/README.md")
    assert manifest["issue_tracker"].endswith("/SUPPORT.md")
    for url in (
        urls["Documentation"],
        urls["Access Mode"],
        urls["Support"],
        urls["Security"],
        manifest["documentation"],
        manifest["issue_tracker"],
    ):
        assert release_ref in url
        assert "/blob/main/" not in url

    for url in (*urls.values(), manifest["issue_tracker"]):
        assert "/discussions" not in url
        assert "/issues" not in url
        assert "/security/policy" not in url
        assert "/security/advisories/new" not in url


def test_docs_first_entrypoints_keep_private_repo_caveat_visible() -> None:
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_links = cast(list[dict[str, object]], issue_config["contact_links"])
    docs_link = next(link for link in contact_links if "Documentation" in str(link["name"]))
    bug_text = _BUG_TEMPLATE.read_text(encoding="utf-8")
    docs_text = _DOCS_README.read_text(encoding="utf-8")

    assert str(docs_link["url"]).endswith("/docs/README.md")
    about_text = str(docs_link["about"]).lower()
    assert "docs-first route stays canonical" in about_text
    assert "repository access" in about_text
    assert "Public Fast Path" in docs_text
    assert "Maintainer Appendix" in docs_text
    assert "SECURITY.md" in bug_text
    assert "docs/README.md" in bug_text
    assert "maintainer-unavailable drill" in bug_text.lower()
    assert "HACS only supports public GitHub repositories" in bug_text
    assert "private" in bug_text.lower() or "私有" in bug_text
