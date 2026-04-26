#!/usr/bin/env python3
"""
Package a skill folder into a .skill file (a zip with a specific layout).

The Anthropic skill format is just a zip archive whose root is the skill's
own folder name (containing SKILL.md + references/ + any other resources).
This script reproduces that layout without depending on the external
skill-creator tooling.

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [<output-dir>]

Example:
    python scripts/package_skill.py skills/odoo19-syntax dist/odoo19-syntax/
"""

from __future__ import annotations

import fnmatch
import re
import sys
import zipfile
from pathlib import Path

# Match skill-creator's exclusion rules
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git"}
EXCLUDE_GLOBS = {"*.pyc", "*.pyo"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
# Subdirectories under the skill root that should not be shipped inside .skill
ROOT_EXCLUDE_DIRS = {"evals"}
# Files at the skill root that are project-management only, not part of the skill
ROOT_EXCLUDE_FILES = {"CHANGELOG.md", "README.md", "build.config.json"}


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if not parts:
        return False
    # Any path containing an excluded dir
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    # Excluded subdirs at the skill root: parts[0] is skill folder name, parts[1] is first subdir
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    if len(parts) == 2 and parts[1] in ROOT_EXCLUDE_FILES:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def validate_skill(skill_path: Path) -> None:
    if not skill_path.is_dir():
        raise SystemExit(f"❌ Not a directory: {skill_path}")
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        raise SystemExit(f"❌ Missing SKILL.md in {skill_path}")
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit("❌ SKILL.md is missing YAML frontmatter (--- ... ---)")
    if not re.search(r"^name:\s*\S+", text, re.MULTILINE):
        raise SystemExit("❌ SKILL.md frontmatter is missing required `name:` field")
    if not re.search(r"^description:\s*\S+", text, re.MULTILINE):
        raise SystemExit("❌ SKILL.md frontmatter is missing required `description:` field")


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    skill_path = skill_path.resolve()
    validate_skill(skill_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}.skill"

    print(f"📦 Packaging {skill_name} → {output_file}")
    skill_root_parent = skill_path.parent

    added = 0
    skipped = 0
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(skill_path.rglob("*")):
            if not item.is_file():
                continue
            rel = item.relative_to(skill_root_parent)
            if should_exclude(rel):
                skipped += 1
                continue
            zf.write(item, arcname=str(rel))
            added += 1

    print(f"   ✅ Added {added} files (skipped {skipped})")
    return output_file


def main() -> None:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(__doc__)
        sys.exit(1)
    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("dist") / skill_path.name
    package_skill(skill_path, output_dir)


if __name__ == "__main__":
    main()
