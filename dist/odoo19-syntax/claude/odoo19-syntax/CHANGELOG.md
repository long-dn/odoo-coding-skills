# Changelog — odoo19-syntax

This file tracks changes to the odoo19-syntax skill specifically. For repo-level changes (build script, infrastructure, etc.), see the top-level `CHANGELOG.md`.

## [0.1.0] — 2026-04

Initial release.

### Coverage

- **ORM** — `models.Constraint`, `Command`, `_compute_display_name`,
  `_read_group` / `formatted_read_group`, `Markup`, `flush_recordset` /
  `invalidate_recordset`, `check_access` / `has_access`, `_search_display_name`,
  `aggregator`, `Domain.OR` and `any` / `not any` operators, `env.tz` /
  `env.company` / `env.companies`, deprecated `_cr` / `_context` / `_uid`,
  `@api.private` (new), `@api.returns` (removed).
- **Views** — `attrs` and `states` removed, `<tree>` → `<list>`, kanban `card`
  template, `t-raw` and `t-esc` both removed (use `t-out`), `t-call` attribute
  syntax, `<chatter/>` shorthand, search-view `<group>` cannot have `string`
  or `expand`.
- **Controllers** — `type='jsonrpc'`, `auth='bearer'`.
- **OWL & JS** — OWL 2 (`useSubEnv`, frozen `env`, no t-ref to children),
  `useService`, `patch`, `useSortable`, POS `getOrder()` rename,
  `request.cart` / `request.pricelist`, CSP enforcement.
- **Manifest, hooks, security** — `license` mandatory, `post_init_hook(env)`
  signature, `xmlrpc_port` → `http_port`, demo data off by default,
  `res.groups.privilege` refactor, `groups_id` → `group_ids`.
- **SCSS** — dart-sass: `math.div(...)`, `@use` / `@forward`.
- **Model & field renames** — `hr.contract` → `hr.version`,
  `procurement.group` → `stock.reference`, `stock.quant.package` →
  `stock.package`, `bus.presence` → `mail.presence`, `hr.candidate` →
  `hr.applicant`, `tax_id` → `tax_ids`, `product_uom` → `product_uom_id`,
  `purchase.order.notes` → `note`, `fleet.vehicle.first_contract_date` →
  `contract_date_start`. Removed: `hr.expense.sheet`, `hr.employee.base`,
  `res.partner.title` (model), `stock.valuation.layer` (model),
  `ir.cron.numbercall`, `res.partner.mobile` / `picking_warn` /
  `last_website_so_id`, `account.move.line.product_uom_category_id`,
  `product.uom.category_id`, `product.template.sale_line_warn`.

### Tested with

11 test prompts in `evals/`.
