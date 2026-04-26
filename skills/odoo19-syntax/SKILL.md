---
name: odoo19-syntax
description: Authoritative reference for Odoo 19 syntax conventions across Python ORM, XML views, OWL/JavaScript, controllers, manifests, and SCSS. Use this skill BEFORE writing or modifying any Odoo code, whenever the user mentions Odoo, an Odoo module, an Odoo model, an XML view, an OWL component, or any file under an Odoo addons directory. Odoo 19 introduces breaking changes (130 model renames, res.groups privilege refactor, hr.contract→hr.version, models.Constraint, attrs removal continued, type='jsonrpc') that older training data does NOT reflect. Always consult this skill before generating code, even if the request looks routine — a model that "obviously" works in Odoo 18 may be wrong in Odoo 19. Trigger this skill on phrases like "create an Odoo module", "add a field to res.partner", "write a controller", "make an OWL component", "fix this Odoo view", "_sql_constraints", "tree view", or any time you see a `__manifest__.py`, `models/*.py`, `views/*.xml`, or `static/src/**/*.js` file in an Odoo project.
---

# Odoo 19 Syntax Skill

This skill ensures generated code matches Odoo 19 (released September 2025) syntax conventions, NOT older versions. Odoo 19 introduces ~130 model renames, the largest schema change since Odoo 14, plus continued enforcement of changes from Odoo 17/18.

## CRITICAL: Detect the version FIRST

**This skill applies ONLY to Odoo 19 projects.** Before suggesting any syntax, determine the project's Odoo version. If the project is NOT Odoo 19, stop using this skill and let the user know — do not silently apply Odoo 19 syntax to an Odoo 17/18 codebase, because it will break.

Detection priority (try in order, stop at the first that works):

### 1. Read `__manifest__.py` of the target module

Look for the `version` field. The first two numbers indicate the Odoo version:

```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',   # ← Odoo 19
    # ...
}
```

- `'19.0.x.x.x'` → Odoo 19, this skill applies.
- `'18.0.x.x.x'`, `'17.0.x.x.x'`, etc. → Different version, **STOP and skip this skill**.
- Missing version field → Continue to step 2.

If multiple `__manifest__.py` files exist, read the one for the module being edited. If unsure which module, check the file path of the user's request (e.g., `addons/sale_custom/models/...` → read `addons/sale_custom/__manifest__.py`).

### 2. Read Odoo source `release.py`

If the project is a full Odoo source checkout, look for `odoo/release.py` or `odoo/__init__.py` containing `version_info`:

```python
version_info = (19, 0, 0, 'final', 0, '')
```

The first integer is the major version.

Common locations to check (use `view` or `bash` `find`):
- `./odoo/release.py`
- `./release.py`
- `./odoo-bin` followed by source tree

### 3. Check `requirements.txt`, `pyproject.toml`, or Docker config

Sometimes the version is pinned via:
- A line like `odoo==19.0.*` in `requirements.txt`
- An image like `odoo:19.0` in `docker-compose.yml` or `Dockerfile`

### 4. Ask the user

If steps 1–3 fail, ask the user directly: "I couldn't auto-detect the Odoo version from the project files. Which version is this — Odoo 19, or something else?" Do not assume Odoo 19 by default.

### Behavior when version ≠ 19

If detection shows the project is Odoo 17, 18, or earlier:
1. Tell the user: "This project appears to be on Odoo X.0, not Odoo 19. I'll skip the Odoo 19 syntax skill and write code matching Odoo X.0 conventions instead."
2. Do NOT load the references in this skill for code generation.
3. Use your general Odoo knowledge for that version.

If the project is Odoo 19 (or version is uncertain and the user confirmed 19), proceed with the rest of this skill.

---

## How to use this skill (once Odoo 19 is confirmed)

The detailed syntax rules are split into reference files by domain. **Load only the references relevant to the current task** — you don't need all of them every time.

| Task involves... | Load this reference |
|---|---|
| Python models, ORM, fields, methods, constraints | `references/orm.md` |
| XML views (form, list/tree, kanban, search), QWeb | `references/views.md` |
| HTTP controllers, routes, RPC endpoints | `references/controllers.md` |
| OWL components, services, JS in `static/src/` | `references/owl_js.md` |
| `__manifest__.py`, hooks, security, asset bundles | `references/manifest_security.md` |
| SCSS files, asset registration | `references/scss_assets.md` |
| Model name lookups (hr.contract? procurement.group?) | `references/model_renames.md` |

**Always load `references/orm.md` and `references/views.md` for any non-trivial Python+XML task** — they're the most frequent source of mistakes.

For model name questions (e.g., "is the model still `hr.contract`?"), `references/model_renames.md` is the source of truth — Odoo 19 renamed 130 models.

## Workflow for a code-generation request

1. **Detect version** (per the section above). If not Odoo 19, exit this skill.
2. **Identify the task domain(s)** — Python? Views? OWL? Controllers? Multiple?
3. **Load relevant references** — read each `references/*.md` file you need.
4. **For any model name** the user mentions or you plan to use, cross-check `references/model_renames.md`. Do not skip this — model renames are the silent-failure category.
5. **Generate code** following the patterns in the references.
6. **Self-check before responding**: scan your draft for these red flags:

   *Constraints, decorators, imports:*
   - `_sql_constraints = [...]` → should be `_constraints = [models.Constraint(...)]` in Odoo 19
   - `from odoo.models import Constraint` → unnecessary; use `models.Constraint(...)` directly
   - `from odoo.fields import Command` → must be `from odoo import Command`
   - `from odoo.osv.expression import OR/AND` → use `Domain.OR` / `Domain.AND` (`from odoo import Domain`)
   - `@api.returns(...)` decorator → REMOVED in Odoo 19, drop it
   - Helper method exposed via RPC by accident → consider `@api.private`

   *Record/env access:*
   - `self._cr` → `self.env.cr`
   - `self._context` → `self.env.context`
   - `self._uid` → `self.env.uid`
   - `self._context.get('tz')` → `self.env.tz`
   - `self._context.get('allowed_company_ids')` → `self.env.companies`

   *Methods:*
   - `name_get(self)` → must be `_compute_display_name(self)`
   - `read_group(...)` → `_read_group(...)` (backend) or `formatted_read_group(...)`
   - `check_access_rights(...)` / `check_access_rule(...)` → `check_access(...)` (combined)
   - `_render_qweb_pdf(...)` → must be `_render(...)`
   - `SavepointCase` import → must be `TransactionCase`
   - `(0, 0, {...})` tuple syntax for O2M/M2M → use `Command.create({...})`

   *Domain syntax:*
   - Uppercase domain operators (`'LIKE'`, `'IN'`, etc.) → must be lowercase
   - Complex relational subqueries via dot-notation → consider `('field_ids', 'any', [...])` operator

   *Views (XML):*
   - `attrs="{...}"` → must be inline `invisible=`, `readonly=`, `required=`
   - `<tree>` → must be `<list>`
   - `<group string="..."` or `<group expand="..."` inside `<search>` view → drop both, leave `<group>` bare
   - `t-raw="..."` → must be `t-out="..."`
   - `t-esc="..."` → REMOVED in Odoo 19, must be `t-out="..."`
   - `<chatter>` boilerplate (3 fields) → use `<chatter/>` shorthand
   - `<t t-call>` with nested `<t t-set>` → use attribute syntax `<t t-call="tpl" var="value"/>`

   *Manifest, hooks, config:*
   - `post_init_hook(cr, registry)` signature → must be `post_init_hook(env)`
   - Manifest missing `'license'` key → required (e.g. `'LGPL-3'`)
   - `xmlrpc_port` in odoo.conf → `http_port`

   *Controllers:*
   - `type="json"` on a route called by the web client → likely should be `type="jsonrpc"`

   *SCSS:*
   - SCSS using `/` for division → must use `math.div(...)` or `calc(...)`
   - SCSS `@import "..."` → must use `@use "..."` (dart-sass)

   *Renamed models (silent failures — see `model_renames.md`):*
   - `hr.contract` → `hr.version`
   - `procurement.group` → `stock.reference`
   - `stock.quant.package` → `stock.package`
   - `bus.presence` → `mail.presence`
   - `hr.candidate` → `hr.applicant`
   - `hr.employee.base` → REMOVED (use `hr.employee`)
   - `res.partner.title` → REMOVED
   - `stock.valuation.layer` → REMOVED (data on `stock.move`)
   - `hr.expense.sheet` → REMOVED

   *Renamed fields:*
   - `groups_id` → `group_ids` (on `res.users`, menus, views, actions, rules)
   - `tax_id` → `tax_ids` on `sale.order.line`; `taxes_id` → `tax_ids` on `purchase.order.line`
   - `product_uom` → `product_uom_id` on sale/purchase lines
   - `purchase.order.notes` → `note`
   - `fleet.vehicle.first_contract_date` → `contract_date_start`

   *Removed fields (delete from code/XML):*
   - `<field name="numbercall">` on `ir.cron` records
   - `res.partner.mobile` (use `phone`), `res.partner.title`, `res.partner.picking_warn`, `res.partner.last_website_so_id`
   - `account.move.line.product_uom_category_id`, `product.uom.category_id`
   - `product.template.sale_line_warn`

   *OWL/JS specific:*
   - `this.pos.get_order()` → `this.pos.getOrder()` (camelCase)
   - `request.website.sale_get_order()` → `request.cart`
   - `request.website.pricelist_id` → `request.pricelist`

If any red flag fires, fix the code before showing it to the user.

## What NOT to do

- Do **not** apply Odoo 19 conventions to projects on older versions.
- Do **not** skip the version-check step "because the user said Odoo 19" — verify by reading at least one project file when possible.
- Do **not** assume `_sql_constraints` is wrong without confirming Odoo 19; it still works in 18 and earlier.
- Do **not** tell the user "this is the Odoo way" without specifying the version — say "in Odoo 19, ..." explicitly.
