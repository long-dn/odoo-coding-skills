# Changelog

Repo-level changes. For changes to individual skills, see each skill's own `CHANGELOG.md` under `skills/<n>/`.

## [0.2.0] — 2026-04

### Added — `npx` installer

Repo can now be published as an npm package; users install skills via `npx odoo-coding-skills`.

- Interactive CLI (`installer/index.js`) prompts for skill, provider, and target dir
- Non-interactive mode via flags (`--skill`, `--provider`, `--target`, `--yes`)
- Conflict detection: warns before overwriting existing files
- Provider-specific post-install hints (Copilot settings, Aider command, etc.)
- `--list` to enumerate available skills, `--help` for usage
- GitHub Action `npm-publish.yml` to automate npm publish on release tags
- Documentation: `docs/publishing.md`

### Reorganized for multi-skill support

- `skill/` → `skills/<n>/` (each skill is a self-contained folder)
- `dist/` → `dist/<n>/<provider>/` (per-skill output)
- `evals/` moved into each skill's folder
- Per-skill `README.md`, `CHANGELOG.md`, and optional `build.config.json`
- New `scripts/new_skill.py` to scaffold skills
- New `scripts/package_skill.py` (no external dependency on skill-creator)
- Updated `scripts/build.py` to handle `--skill <n>` and `--list` flags

## [0.1.0] — 2026-04

Initial release with single skill `odoo19-syntax`.
