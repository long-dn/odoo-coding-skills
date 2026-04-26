# odoo-coding-skills

Odoo coding skills for AI coding agents, distributed in the standard `SKILL.md` format.

This repository is installed with the open `skills` CLI only. It does not ship a custom `npx odoo-coding-skills` installer and does not maintain provider-specific generated files.

## Install

Install the Odoo 19 syntax skill into the current project:

```bash
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax
```

Install it globally for your user:

```bash
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax --global
```

Install for specific supported agents:

```bash
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax --agent codex
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax --agent claude-code
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax --agent cursor
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax --agent github-copilot
npx skills add long-dn/odoo-coding-skills --skill odoo19-syntax --agent gemini-cli
```

Supported agents in this repo:

| Agent | `skills` CLI agent id |
|---|---|
| Codex | `codex` |
| Gemini CLI | `gemini-cli` |
| Claude Code | `claude-code` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |

## Available Skills

| Skill | What it covers | Status |
|---|---|---|
| [`odoo19-syntax`](./skills/odoo19-syntax/) | Odoo 19 backend Python/ORM, XML views, OWL/JS, controllers, manifest, SCSS, and model renames | Stable |

## How It Works

Each skill lives under `skills/<name>/` and contains a standard `SKILL.md` file with YAML frontmatter:

```text
skills/odoo19-syntax/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── references/
```

The `npx skills add ...` command reads this repository and installs the selected skill into the target agent's skill directory. Agent-specific paths and symlinking/copying are handled by the `skills` CLI.

Manual test prompts live outside the installable skill folders under `evals/<skill-name>/`.

## Add a New Skill

```bash
python scripts/new_skill.py my-new-skill --description "When to use this skill"
```

Then edit the generated files under `skills/my-new-skill/` and add a row to the Available Skills table above.

## Validate

```bash
npx skills add . --list
npx skills add . --skill odoo19-syntax --agent codex --copy
```

## License

MIT. See [LICENSE](./LICENSE).
