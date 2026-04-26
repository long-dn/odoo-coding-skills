# Authoring A New Skill

This guide walks through creating a new standard `SKILL.md` skill.

## Anatomy

A skill is a folder under `skills/<name>/`:

```text
skills/my-skill/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── references/
    ├── domain-a.md
    └── domain-b.md
```

Manual evals live outside the installable skill folder:

```text
evals/my-skill/
└── 01_some_test.md
```

`SKILL.md` is required. `references/` keeps large rule sets split by topic. Keep evals outside `skills/<name>/` because `npx skills add ...` copies the full skill folder into agent directories.

## Scaffold

```bash
python scripts/new_skill.py my-skill --description "When the assistant should use this skill"
```

Then edit the generated files.

## Write `SKILL.md`

`SKILL.md` should:

- Have YAML frontmatter with `name` and `description`.
- Explain when the skill applies.
- Define version or context detection when relevant.
- Route the assistant to the right files under `references/`.
- Include a short self-check list of common mistakes.

The `description` is the main trigger signal. Make it specific and mention concrete phrases, files, APIs, or framework versions that should activate the skill.

## Write References

Each `references/*.md` file should cover one domain. Use concrete examples and show wrong versus correct patterns when possible.

Good references usually include:

- The old pattern to avoid.
- The correct replacement.
- Required imports or configuration.
- The failure mode if the rule is ignored.

## Write Evals

Every important rule should have at least one test prompt under `evals/<skill-name>/`.

Recommended format:

```markdown
# Test Case N: Short title

## User Prompt

The actual prompt a user might send.

## Project context

Any necessary context.

## What we're testing

- Behavior 1
- Behavior 2

## Expected output

What the assistant should produce.

## Anti-patterns to flag

- Common mistake 1
- Common mistake 2
```

## Validate Installability

From the repo root:

```bash
npx skills add . --list
npx skills add . --skill my-skill --agent codex --copy
```

Use the `--agent` ids documented in the top-level README.

## Publish

Commit the skill folder under `skills/<name>/` and update the top-level README's Available Skills table.
