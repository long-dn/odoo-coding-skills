# odoo19-syntax

> A version-aware Odoo 19 coding-rules pack. Tells the AI assistant to detect the project's Odoo version first, **skip** if it's not 19, and otherwise apply the correct syntax for every domain.

Odoo 19 introduced ~130 model renames and a long list of breaking syntax changes (`_sql_constraints` → `models.Constraint`, `attrs` removed, `<tree>` → `<list>`, `t-esc` removed, `hr.contract` → `hr.version`, `groups_id` → `group_ids`, …). LLM coding assistants trained before Odoo 19's release happily emit Odoo 17 / 18 syntax that silently breaks.

## What it covers

Seven domains:

- **ORM** — `models.Constraint`, `Command`, `_compute_display_name`, `_read_group` / `formatted_read_group`, `Markup`, `Domain.OR` and `any` / `not any` operators, `env.tz` / `env.company` / `env.companies`, deprecated `_cr` / `_context` / `_uid`, `@api.private` (new), `@api.returns` (removed).
- **Views** — `attrs` and `states` removed, `<tree>` → `<list>`, kanban `card` template, `t-raw` and `t-esc` both removed (use `t-out`), `t-call` attribute syntax, `<chatter/>` shorthand, search-view `<group>` cannot have `string` or `expand`.
- **Controllers** — `type='jsonrpc'` for web-client RPC, `auth='bearer'` for tokens.
- **OWL & JS** — OWL 2 patterns, plain `rpc` import from `@web/core/network/rpc`, `useService`, `useSubEnv`, `patch`, `useSortable`, POS `getOrder()` (camelCase), `request.cart` / `request.pricelist`, CSP rules.
- **Manifest, hooks, security** — `license` mandatory, `post_init_hook(env)` signature, `groups_id` → `group_ids`, `res.groups.privilege`, `xmlrpc_port` → `http_port`, demo data not loaded by default.
- **SCSS** — dart-sass, `math.div(...)`, `@use` / `@forward`.
- **Model & field renames** — full table of the 130 model renames + 51 field renames + removed models/fields. The category most likely to silently break LLM-generated code.

See `SKILL.md` for the full self-check checklist.

## Install

Install with the standard `skills` CLI:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax
```

Odoo version is selected by skill name. This skill is for Odoo 19 only. If this repo adds other Odoo versions later, install the matching skill name, for example `odoo18-syntax` or `odoo20-syntax`.

Install for a specific supported agent:

```bash
npx skills add long-dn/odoo-version-skills --skill odoo19-syntax --agent codex
```

Supported agent ids:

| Tool | `skills` CLI agent id |
|---|---|
| Codex | `codex` |
| Gemini CLI | `gemini-cli` |
| Claude Code | `claude-code` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |

## Tested with

11 test prompts covering:

1. SQL constraints (`models.Constraint` pattern)
2. View migration (`attrs`/`states`/`tree` removal)
3. HTTP controllers + OWL components (jsonrpc + plain rpc function)
4. Model rename trap (`hr.contract` → `hr.version`)
5. **Version check on Odoo 17 project** (must skip the skill)
6. Command objects for O2M/M2M
7. `ir.cron` `numbercall` removal
8. Search view `<group>` without `string`/`expand`
9. Deprecated `_context` / `_cr` / `_uid` migration
10. `tax_id` / `product_uom` field renames on order lines
11. Domain `any` operator + `Domain.OR`

See `../../evals/odoo19-syntax/` for the prompts in this repository.

## Modify and validate

Edit `SKILL.md` or any `references/*.md`, then from the repo root:

```bash
npx skills add . --list
```

To validate behavior after changes, manually run a few of the `evals/*.md` prompts against an installed skill and confirm the assistant produces the expected output.

## Sources

Compiled from:

- Official Odoo 19 documentation (changelog, ORM reference, mixins reference)
- OCA OpenUpgrade migration analysis for 19.0
- Cybrosys, Ksolves, OCU Odoo 19 dev write-ups
- Medium migration series by Osama Alhalabi (Odoo 16 → 19 backend overhaul)
- `odoo/odoo` 19.0 source on GitHub (domains.py, mail mixins)
