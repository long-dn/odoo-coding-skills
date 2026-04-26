#!/usr/bin/env python3
"""
Build provider-specific distributions for every skill in `skills/`.

For each skill `skills/<name>/`, this generates `dist/<name>/<provider>/`
adapter files plus a `dist/<name>/<name>.skill` package, ready to publish.

Usage:
    python scripts/build.py                  # build all skills
    python scripts/build.py --skill odoo19-syntax    # build one skill
    python scripts/build.py --list           # list available skills
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
DIST_DIR = ROOT / "dist"

sys.path.insert(0, str(ROOT / "scripts"))
from package_skill import package_skill  # noqa: E402


# ---------- Per-skill load + adapter logic ----------

def discover_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def strip_yaml_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:].lstrip("\n")
    return text


def extract_skill_metadata(skill_md: str) -> dict:
    m = re.search(r"^---\n(.*?)\n---\n", skill_md, re.DOTALL)
    if not m:
        return {"name": "unknown", "description": ""}
    block = m.group(1)
    meta = {}
    name_m = re.search(r"^name:\s*(.+?)$", block, re.MULTILINE)
    if name_m:
        meta["name"] = name_m.group(1).strip().strip('"')
    desc_m = re.search(
        r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", block, re.MULTILINE | re.DOTALL
    )
    if desc_m:
        desc = desc_m.group(1).strip()
        if desc.startswith('"') and desc.endswith('"'):
            desc = desc[1:-1]
        meta["description"] = re.sub(r"\s+", " ", desc)
    return meta


def load_skill(skill_path: Path) -> dict:
    skill_md = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    meta = extract_skill_metadata(skill_md)
    body = strip_yaml_frontmatter(skill_md)

    refs_dir = skill_path / "references"
    references = {}
    if refs_dir.is_dir():
        for ref_file in sorted(refs_dir.glob("*.md")):
            references[ref_file.stem] = ref_file.read_text(encoding="utf-8")

    # Optional skill-level config to override defaults
    config_path = skill_path / "build.config.json"
    config = {}
    if config_path.is_file():
        import json
        config = json.loads(config_path.read_text(encoding="utf-8"))

    return {
        "path": skill_path,
        "name": skill_path.name,
        "meta_name": meta.get("name", skill_path.name),
        "description": meta.get("description", ""),
        "body": body,
        "references": references,
        "config": config,
    }


# ---------- Globs for routing rules to relevant files ----------

DEFAULT_DOMAIN_GLOBS = {"_default": ["**/*.py", "**/*.xml", "**/*.js"]}


def resolve_globs(skill: dict, ref_name: str) -> list[str]:
    """Look up scoping globs for a reference file. Skills can override via build.config.json:
    {"globs": {"orm": ["**/models/**/*.py"], ...}}"""
    config_globs = skill.get("config", {}).get("globs", {})
    if ref_name in config_globs:
        return config_globs[ref_name]
    return DEFAULT_DOMAIN_GLOBS.get(ref_name, ["**/*"])


def reference_titles(skill: dict) -> dict:
    """Skill can declare friendly titles via build.config.json:
    {"reference_titles": {"orm": "ORM, Models, Fields"}}"""
    return skill.get("config", {}).get("reference_titles", {})


def reference_order(skill: dict) -> list[str]:
    """Skill can pin reference ordering via build.config.json:
    {"reference_order": ["orm", "views", ...]}. Defaults to alpha order."""
    declared = skill.get("config", {}).get("reference_order")
    if declared:
        return [r for r in declared if r in skill["references"]]
    return sorted(skill["references"].keys())


def title_for(skill: dict, ref_name: str) -> str:
    return reference_titles(skill).get(ref_name, ref_name.replace("_", " ").title())


# ---------- Combined-markdown helper ----------

def build_combined_markdown(skill: dict) -> str:
    parts = []
    parts.append(f"# {skill['meta_name']} — coding rules\n")
    parts.append((skill["description"] or "").strip() + "\n")
    parts.append("---\n")
    parts.append("## Workflow & version detection\n")
    parts.append(skill["body"].strip() + "\n")
    parts.append("---\n")
    for name in reference_order(skill):
        body = skill["references"][name]
        body = re.sub(r"^(#+) ", lambda m: "#" + m.group(1) + " ", body, flags=re.MULTILINE)
        parts.append(f"## {title_for(skill, name)}\n")
        parts.append(body.strip() + "\n")
        parts.append("---\n")
    return "\n".join(parts).rstrip() + "\n"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------- Provider builders ----------

def build_claude(skill: dict, out: Path) -> None:
    target = out / skill["name"]
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(skill["path"], target, ignore=shutil.ignore_patterns("evals", "__pycache__", "build.config.json"))
    readme = (
        f"# Claude / Anthropic — {skill['meta_name']}\n\n"
        f"This folder mirrors the canonical skill source. The pre-packaged "
        f"`{skill['name']}.skill` file in the parent directory is the upload-ready archive.\n\n"
        "## Install (Claude.ai)\n\n"
        "Settings → Capabilities → Skills → Upload skill → choose the `.skill` file.\n\n"
        "## Install (Claude Code CLI)\n\n"
        f"Place this `{skill['name']}/` folder under your project's `.claude/skills/` directory.\n"
    )
    write(out / "README.md", readme)


def build_cursor(skill: dict, out: Path) -> None:
    master_globs = ["**/__manifest__.py", "**/*.py", "**/*.xml", "**/static/src/**/*"]
    master_frontmatter = (
        "---\n"
        f"description: {skill['description'][:200]}\n"
        f"globs: {master_globs}\n"
        "alwaysApply: false\n"
        "---\n\n"
    )
    write(
        out / ".cursor" / "rules" / f"{skill['name']}-master.mdc",
        master_frontmatter + skill["body"].strip() + "\n",
    )

    for name in reference_order(skill):
        title = title_for(skill, name)
        globs = resolve_globs(skill, name)
        fm = (
            "---\n"
            f"description: {skill['meta_name']} — {title}.\n"
            f"globs: {globs}\n"
            "alwaysApply: false\n"
            "---\n\n"
        )
        write(out / ".cursor" / "rules" / f"{skill['name']}-{name}.mdc", fm + skill["references"][name])

    write(
        out / "README.md",
        "# Cursor distribution\n\n"
        "Drop the `.cursor/` directory into the **root of your project**. "
        "Cursor auto-attaches the matching rule when you edit a file matching its globs.\n",
    )


def build_copilot(skill: dict, out: Path) -> None:
    write(out / ".github" / "copilot-instructions.md", build_combined_markdown(skill))
    for name in reference_order(skill):
        globs = resolve_globs(skill, name)
        apply_to = ",".join(globs)
        fm = f'---\napplyTo: "{apply_to}"\n---\n\n'
        write(
            out / ".github" / "instructions" / f"{skill['name']}-{name}.instructions.md",
            fm + skill["references"][name],
        )

    write(
        out / "README.md",
        "# GitHub Copilot distribution\n\n"
        "## Repo-wide single file (simpler)\n\n"
        "Copy `.github/copilot-instructions.md` to your project's `.github/`.\n\n"
        "Enable in VS Code:\n\n"
        "```json\n"
        '{ "github.copilot.chat.codeGeneration.useInstructionFiles": true }\n'
        "```\n\n"
        "## Scoped instructions (more accurate)\n\n"
        "Copy `.github/instructions/*.instructions.md` to your project. Each file declares "
        "`applyTo` globs so Copilot only loads the relevant rule for matching files.\n",
    )


def build_cline(skill: dict, out: Path) -> None:
    write(out / ".clinerules", build_combined_markdown(skill))
    split = out / ".clinerules-split"
    write(split / "00-master.md", "# Master rules\n\n" + skill["body"].strip() + "\n")
    for i, name in enumerate(reference_order(skill), start=1):
        write(split / f"{i:02d}-{name}.md", f"# {title_for(skill, name)}\n\n" + skill["references"][name])

    write(
        out / "README.md",
        "# Cline distribution\n\n"
        "## Single file\n\nCopy `.clinerules` to your project root.\n\n"
        "## Multi-file (recommended for large rulesets)\n\n"
        "Rename `.clinerules-split/` to `.clinerules/` and place at your project root.\n",
    )


def build_windsurf(skill: dict, out: Path) -> None:
    write(out / ".windsurfrules", build_combined_markdown(skill))
    write(
        out / "README.md",
        "# Windsurf / Codeium distribution\n\n"
        "Copy `.windsurfrules` to your project root.\n",
    )


def build_aider(skill: dict, out: Path) -> None:
    write(out / "CONVENTIONS.md", build_combined_markdown(skill))
    write(out / ".aider.conf.yml.example", "read:\n  - CONVENTIONS.md\n")
    write(
        out / "README.md",
        "# Aider distribution\n\n"
        "Copy `CONVENTIONS.md` to your project root.\n\n"
        "Run aider with `aider --read CONVENTIONS.md`, or copy "
        "`.aider.conf.yml.example` to `.aider.conf.yml` to load automatically.\n",
    )


def build_continue(skill: dict, out: Path) -> None:
    base = out / ".continue" / "rules"
    write(base / f"00-{skill['name']}-master.md", skill["body"].strip() + "\n")
    for i, name in enumerate(reference_order(skill), start=1):
        write(
            base / f"{i:02d}-{skill['name']}-{name}.md",
            f"# {skill['meta_name']} — {title_for(skill, name)}\n\n" + skill["references"][name],
        )
    write(
        out / "README.md",
        "# Continue.dev distribution\n\nCopy `.continue/rules/` to your project root.\n",
    )


def build_generic(skill: dict, out: Path) -> None:
    combined = build_combined_markdown(skill)
    write(out / f"{skill['name']}.md", combined)
    per_domain = out / "per-domain"
    write(per_domain / "00-master.md", "# Master rules\n\n" + skill["body"].strip() + "\n")
    for name in reference_order(skill):
        write(per_domain / f"{name}.md", f"# {title_for(skill, name)}\n\n" + skill["references"][name])
    write(
        out / "README.md",
        "# Generic distribution — works with any LLM\n\n"
        f"Paste `{skill['name']}.md` into ChatGPT custom instructions, Gemini system "
        "prompt, an LLM API `system` parameter, or any agent rules field.\n\n"
        "Use `per-domain/` files individually if your target has a system-prompt size limit.\n",
    )


PROVIDERS = [
    ("claude", build_claude),
    ("cursor", build_cursor),
    ("copilot", build_copilot),
    ("cline", build_cline),
    ("windsurf", build_windsurf),
    ("aider", build_aider),
    ("continue", build_continue),
    ("generic", build_generic),
]


def build_one(skill_path: Path) -> None:
    print(f"\n🔨 Building {skill_path.name}...")
    skill = load_skill(skill_path)
    skill_dist = DIST_DIR / skill["name"]
    if skill_dist.exists():
        shutil.rmtree(skill_dist)

    for provider_name, fn in PROVIDERS:
        fn(skill, skill_dist / provider_name)
        print(f"   ✅ {provider_name}")

    package_skill(skill["path"], skill_dist)


# ---------- CLI ----------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", help="Build only this skill (folder name under skills/)")
    parser.add_argument("--list", action="store_true", help="List available skills")
    args = parser.parse_args()

    skills = discover_skills()
    if not skills:
        print("No skills found under skills/. Use scripts/new_skill.py to create one.")
        sys.exit(0)

    if args.list:
        print("Available skills:")
        for s in skills:
            meta = extract_skill_metadata((s / "SKILL.md").read_text(encoding="utf-8"))
            print(f"  - {s.name}  ({meta.get('description', '')[:80]}...)")
        return

    if args.skill:
        target = SKILLS_DIR / args.skill
        if target not in skills:
            print(f"❌ Skill not found: {args.skill}")
            print("Available:", ", ".join(s.name for s in skills))
            sys.exit(1)
        build_one(target)
    else:
        for s in skills:
            build_one(s)

    print(f"\n✅ Done. Output at {DIST_DIR}")


if __name__ == "__main__":
    main()
