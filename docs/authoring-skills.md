# Authoring a new skill

This guide walks through creating a new skill from scratch.

## Anatomy of a skill

A skill is a folder under `skills/<n>/` with this layout:

```
skills/my-skill/
├── SKILL.md             # required — Anthropic skill format with YAML frontmatter
├── README.md            # required — install + coverage docs
├── CHANGELOG.md         # required — per-skill version history
├── build.config.json    # optional — overrides for the build script
├── references/          # required — domain-split rule files
│   ├── domain-a.md
│   └── domain-b.md
└── evals/               # optional but strongly recommended — test prompts
    └── 01_some_test.md
```

The build script reads `SKILL.md` + `references/*.md` and produces adapter files for every supported AI tool. `evals/` is excluded from all distributions — those are tests for you, not part of the rules the assistant sees.

## 1. Scaffold

```bash
python scripts/new_skill.py my-skill --description "When the assistant should use this skill"
```

This creates the folder with template files. Edit them to fit your skill.

## 2. Write SKILL.md

`SKILL.md` is the entry point the AI sees first. It should:

- Have YAML frontmatter with `name` (matches folder name) and `description` (when to trigger).
- Open with a one-paragraph summary.
- If applicable, define a **version detection** workflow: how to confirm the skill applies before applying its rules. This is critical for framework-version skills — without it, the skill will incorrectly apply to wrong versions.
- Route to the right `references/*.md` file based on task type.
- End with a **self-check checklist** of red flags to scan for before responding.

Keep `SKILL.md` under 500 lines. The detail belongs in `references/`.

### A good `description`

The description is the primary triggering signal. Make it specific:

❌ "Helps with Odoo development"
✅ "Authoritative reference for Odoo 19 syntax conventions across Python ORM, XML views, OWL/JavaScript, controllers, manifests, and SCSS. Use BEFORE writing or modifying any Odoo code; Odoo 19 introduces breaking changes that older training data does NOT reflect."

Mention specific phrases ("Odoo 19", "_sql_constraints", "tree view") that should trigger the skill.

## 3. Write reference files

Each `references/*.md` file covers one domain. The file naming and ordering matter — they show up in `build.config.json` and in generated rule files.

Format:

```markdown
# <Skill name> — <domain> reference

Brief intro.

## Table of contents
1. Topic A
2. Topic B
...

## 1. Topic A

Code examples comparing OLD vs ✅ NEW patterns:

\`\`\`python
# ❌ OLD
old_code()

# ✅ Correct
new_code()
\`\`\`

Plain prose explanation of why.
```

Best practices:

- **Always show OLD vs NEW.** AIs learn from contrast better than from a description.
- **Include the import statement** when the change involves a renamed module.
- **Note the failure mode.** "Will silently produce wrong results", "raises ImportError", "fails at module install" — this primes the assistant to take the rule seriously.
- **Use concrete examples.** Not "use the new API" but "use `models.Constraint(...)` instead of `_sql_constraints`".

## 4. Configure build.config.json (optional)

By default the build script:

- Loads references in alphabetical order.
- Generates friendly titles by Title-Casing the filename.
- Uses very broad globs (`**/*`) for Cursor/Copilot scoped rules.

For skills where this matters, override via `build.config.json`:

```json
{
  "reference_order": ["orm", "views", "controllers"],
  "reference_titles": {
    "orm": "ORM, Models, Fields & Methods"
  },
  "globs": {
    "orm": ["**/models/**/*.py"],
    "views": ["**/views/**/*.xml"]
  }
}
```

`globs` is what Cursor and Copilot use to decide when to inject a particular rule. Tighter globs = less noise in the AI's context.

## 5. Write evals

Every rule should have at least one test prompt under `evals/`. Format:

```markdown
# Test Case N: Short title

## User Prompt

The actual prompt a user might send.

## Project context

Any necessary context (e.g., manifest version).

## What we're testing

- Behavior 1
- Behavior 2

## Expected output

What the assistant should produce.

## Anti-patterns to flag

- Common mistake 1
- Common mistake 2
```

To validate, run the prompt against the rebuilt skill in your AI tool and compare to the expected output. There's no automated runner yet — this is a manual review step.

## 6. Build

```bash
python scripts/build.py --skill my-skill
```

This generates `dist/my-skill/` with adapter files for every provider. Spot-check the output, especially the `dist/my-skill/cursor/.cursor/rules/*.mdc` files (the frontmatter format is finicky) and the `.skill` archive (open it to confirm contents).

## 7. Update README and CHANGELOG

Edit `skills/my-skill/README.md` to describe what the skill covers and how to install per-provider.

Edit `skills/my-skill/CHANGELOG.md` with the version (start at 0.1.0).

## 8. Add to top-level README

Add a row to the "Available skills" table in the top-level `README.md`.

## 9. Commit and PR

Commit both `skills/my-skill/` and the regenerated `dist/my-skill/`. The CI workflow checks that `dist/` is in sync with `skills/`.

## Tips for good skills

- **Be specific to a version.** Skills that try to cover "all versions of X" become diluted and unreliable. One skill per major version produces tighter rules.
- **Detect first, apply second.** Always verify context (version, framework, file type) before applying rules. The version-detection step in `SKILL.md` is what prevents the skill from breaking other projects.
- **Cover the silent failures.** The most valuable rules catch errors that don't raise — model name typos, deprecated APIs that still "work" but emit warnings, type-mismatched arguments. These are exactly what AIs miss.
- **Update on framework releases.** Skills go stale fast. Pin a maintenance plan in the README.
