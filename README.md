# odoo-version-skills

Version-aware Odoo skills for AI coding agents, distributed in the standard `SKILL.md` format.

This repository is installed with the open `skills` CLI only:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax
```

It does not publish a custom npm package, does not ship a custom installer, and does not maintain generated provider-specific files.

## Available Skills

| Odoo version | Skill | What it covers | Status |
|---|---|---|---|
| 19 | [`odoo19-syntax`](./skills/odoo19-syntax/) | Odoo 19 backend Python/ORM, XML views, OWL/JS, controllers, manifest, SCSS, and model renames | Stable |

The Odoo version is selected by skill name. The `skills` CLI does not support repository-specific flags like `--odoo-version 19`, so each supported Odoo version should be added as its own skill, for example `odoo18-syntax`, `odoo19-syntax`, and later `odoo20-syntax`.

## Supported Agents

| Agent | `skills` CLI agent id |
|---|---|
| Codex | `codex` |
| Gemini CLI | `gemini-cli` |
| Claude Code | `claude-code` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |

`npx skills add` supports many more agents. This repo only documents and validates the five agents above.

## Install

### Project Install

Install Odoo 19 skill into the current project:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax
```

Install into the current project without prompts for all documented agents:

```bash
npx skills add long-dn/odoo-version-skills \
  --skill odoo19-syntax \
  --agent codex \
  --agent gemini-cli \
  --agent claude-code \
  --agent cursor \
  --agent github-copilot \
  --yes
```

Install for one project agent:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax --agent codex --yes
```

Project installs normally place universal-agent skills under `.agents/skills/` and Claude Code skills under `.claude/skills/`. Exact paths are controlled by the `skills` CLI.

### Global Install

Install Odoo 19 skill globally for your user:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax --global
```

Install globally for all documented agents without prompts:

```bash
npx skills add long-dn/odoo-version-skills \
  --skill odoo19-syntax \
  --agent codex \
  --agent gemini-cli \
  --agent claude-code \
  --agent cursor \
  --agent github-copilot \
  --global \
  --yes
```

Install globally for one agent:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax --agent codex --global --yes
```

## Uninstall

For uninstall commands, run them from the project root when removing a project install. Add `--global` when removing a global install.

### Project Uninstall

Remove `odoo19-syntax` from the current project interactively:

```bash
npx skills remove odoo19-syntax
```

Remove from all documented project agents without prompts:

```bash
npx skills remove odoo19-syntax \
  --agent codex \
  --agent gemini-cli \
  --agent claude-code \
  --agent cursor \
  --agent github-copilot \
  --yes
```

Remove from one project agent:

```bash
npx skills remove odoo19-syntax --agent codex --yes
```

### Global Uninstall

Remove `odoo19-syntax` globally for your user:

```bash
npx skills remove odoo19-syntax --global
```

Remove globally from all documented agents without prompts:

```bash
npx skills remove odoo19-syntax \
  --agent codex \
  --agent gemini-cli \
  --agent claude-code \
  --agent cursor \
  --agent github-copilot \
  --global \
  --yes
```

Remove globally from one agent:

```bash
npx skills remove odoo19-syntax --agent codex --global --yes
```

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

## Add a New Odoo Version Skill

```bash
python scripts/new_skill.py odoo20-syntax --description "When to use Odoo 20 syntax rules"
```

Then edit the generated files under `skills/odoo20-syntax/`, add evals under `evals/odoo20-syntax/`, and add a row to the Available Skills table above.

## Validate

```bash
npx skills add . --list
npx skills add . --skill odoo19-syntax --agent codex --copy --yes
```

## License

MIT. See [LICENSE](./LICENSE).
