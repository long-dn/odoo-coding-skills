# odoo-coding-skills

> A collection of version-aware, framework-specific coding-rules packs for AI assistants. Built once in the canonical Anthropic skill format, distributed automatically to every major AI coding tool.

The problem: LLM coding assistants emit syntax that's confidently wrong when a framework has just released a major version. Odoo 19's `models.Constraint` replaces `_sql_constraints`. React 19's compiler changes how `useMemo` should be used. Tailwind 4 dropped `tailwind.config.js`. The list goes on.

The fix: hand the assistant a small, focused rules pack that says "if the project is on version X, follow these specific rules; otherwise, skip me." This repo collects such packs and distributes them to wherever you run your AI assistant.

## Quick install — `npx odoo-coding-skills`

```bash
cd your-project
npx odoo-coding-skills
```

You'll get an interactive picker:

```
? Which skill do you want to install? › odoo19-syntax
? Which AI tool are you using?        › Cursor
? Project root path:                  › /path/to/your-project
✅ Installed odoo19-syntax for Cursor
   8 files copied to /path/to/your-project
```

Or non-interactive (CI / scripts):

```bash
npx odoo-coding-skills --skill odoo19-syntax --provider cursor --target . -y
npx odoo-coding-skills --list                # list available skills
npx odoo-coding-skills --help                # show all options
```

Supported providers: `claude`, `cursor`, `copilot`, `cline`, `windsurf`, `aider`, `continue`, `generic`.

The `claude` provider downloads the `.skill` file you upload at Claude.ai → Settings → Capabilities → Skills. Other providers drop their config files (`.cursor/`, `.github/copilot-instructions.md`, `.clinerules`, etc.) into your project root automatically.

## Manual install (no Node)

If you don't have Node.js, the same files are checked into `dist/` in this repo. Clone it and copy the relevant `dist/<skill>/<provider>/` folder contents into your project. Each `dist/<skill>/<provider>/README.md` has the per-tool details.

## Available skills

| Skill | What it covers | Status |
|---|---|---|
| [`odoo19-syntax`](./skills/odoo19-syntax/) | Odoo 19 backend (Python/ORM), XML views, OWL/JS, controllers, manifest, SCSS, ~130 model renames | ✅ Stable |

(More skills planned. PRs welcome.)

## How it works

Each skill lives under `skills/<n>/` in the **Anthropic skill format** (a `SKILL.md` with YAML frontmatter plus a `references/` folder). That format is the single source of truth.

`scripts/build.py` reads each skill and generates adapter files for every supported AI tool, dropped into `dist/<skill>/<provider>/`:

| Provider | Output | Where it goes in your project |
|---|---|---|
| Claude / Anthropic | `<skill>.skill` package | Upload via Claude.ai Settings, or place under `.claude/skills/` |
| Cursor | `.cursor/rules/*.mdc` (split per domain, with globs) | Project root |
| GitHub Copilot | `.github/copilot-instructions.md` + scoped `instructions/*.md` | Project root |
| Cline | `.clinerules` (single file) or `.clinerules-split/` (multi-file) | Project root |
| Windsurf / Codeium | `.windsurfrules` | Project root |
| Aider | `CONVENTIONS.md` + `.aider.conf.yml` example | Project root |
| Continue.dev | `.continue/rules/*.md` | Project root |
| Generic (any LLM) | `<skill>.md` — one self-contained markdown | Paste into any system-prompt field |

The build is idempotent and reproducible — running `python scripts/build.py` always produces the same output for the same source.

## Add a new skill

```bash
python scripts/new_skill.py my-new-skill --description "When to apply this skill"
```

This scaffolds `skills/my-new-skill/` with a template `SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`, and `evals/`. Fill in the templates, then:

```bash
python scripts/build.py --skill my-new-skill
```

See [`docs/authoring-skills.md`](./docs/authoring-skills.md) for the full guide.

## Repository layout

```
odoo-coding-skills/
├── README.md                   # this file
├── LICENSE                     # MIT
├── CHANGELOG.md                # repo-level changes
├── package.json                # npm metadata for the npx installer
├── installer/index.js          # the CLI you run via npx
├── skills/                     # ⭐ each skill is a self-contained folder
│   └── odoo19-syntax/
│       ├── SKILL.md            # canonical Anthropic skill source
│       ├── README.md           # skill-specific install + coverage docs
│       ├── CHANGELOG.md        # skill-specific version history
│       ├── build.config.json   # optional skill-level build overrides
│       ├── references/*.md     # the actual rules, split by domain
│       └── evals/*.md          # test prompts to validate behavior
├── dist/                       # generated outputs, one folder per skill
│   └── odoo19-syntax/
│       ├── odoo19-syntax.skill # ready for Claude upload
│       ├── claude/  cursor/  copilot/  cline/  windsurf/  aider/  continue/  generic/
├── scripts/
│   ├── build.py                # build all skills, or one with --skill X
│   ├── new_skill.py            # scaffold a new skill
│   └── package_skill.py        # zip a skill into .skill (no external deps)
├── docs/
│   └── authoring-skills.md     # how to write a new skill
└── .github/workflows/
    ├── build-dist.yml          # CI rebuilds dist/ on push
    └── npm-publish.yml         # publishes to npm on release tags
```

## Build commands

```bash
# Build everything
python scripts/build.py

# Build one skill
python scripts/build.py --skill odoo19-syntax

# List available skills
python scripts/build.py --list

# Scaffold a new skill
python scripts/new_skill.py my-skill-name

# Manually package a single skill into .skill
python scripts/package_skill.py skills/odoo19-syntax dist/odoo19-syntax/
```

## Contributing

1. Fork and clone.
2. Add or modify a skill under `skills/<n>/`.
3. Run `python scripts/build.py --skill <n>` to regenerate `dist/`.
4. Validate with the test prompts in the skill's `evals/` folder.
5. Commit both `skills/` and `dist/` changes.
6. Open a PR.

The CI workflow checks that `dist/` is in sync with `skills/` on every PR.

## License

MIT — see [LICENSE](./LICENSE). Use freely in private and commercial projects.
