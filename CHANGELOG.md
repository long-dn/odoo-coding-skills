# Changelog

Repo-level changes. For changes to individual skills, see each skill's own `CHANGELOG.md` under `skills/<name>/`.

## [0.3.0] - 2026-04

### Changed

- Switched installation to the standard `npx skills add ...` workflow only.
- Removed the custom `npx odoo-coding-skills` installer.
- Removed generated provider distributions under `dist/`.
- Limited documented support to Codex, Gemini CLI, Claude Code, Cursor, and GitHub Copilot through the `skills` CLI agent ids.

## [0.2.0] - 2026-04

### Added

- Initial npm-based installer and provider-specific generated distributions.

## [0.1.0] - 2026-04

Initial release with single skill `odoo19-syntax`.
