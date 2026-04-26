# odoo19-syntax — coding rules

Authoritative reference for Odoo 19 syntax conventions across Python ORM, XML views, OWL/JavaScript, controllers, manifests, and SCSS. Use this skill BEFORE writing or modifying any Odoo code, whenever the user mentions Odoo, an Odoo module, an Odoo model, an XML view, an OWL component, or any file under an Odoo addons directory. Odoo 19 introduces breaking changes (130 model renames, res.groups privilege refactor, hr.contract→hr.version, models.Constraint, attrs removal continued, type='jsonrpc') that older training data does NOT reflect. Always consult this skill before generating code, even if the request looks routine — a model that "obviously" works in Odoo 18 may be wrong in Odoo 19. Trigger this skill on phrases like "create an Odoo module", "add a field to res.partner", "write a controller", "make an OWL component", "fix this Odoo view", "_sql_constraints", "tree view", or any time you see a `__manifest__.py`, `models/*.py`, `views/*.xml`, or `static/src/**/*.js` file in an Odoo project.

---

## Workflow & version detection

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

---

## ORM, Models, Fields & Methods

## Odoo 19 — Python ORM Reference

This reference covers Python model code: fields, methods, constraints, ORM operations.

### Table of contents
1. SQL constraints — `_sql_constraints` → `models.Constraint`
2. Display name — `name_get()` → `_compute_display_name`
3. Command objects (replace tuple syntax for O2M/M2M)
4. `_read_group()` API (replaces `read_group()`)
5. `Markup()` for HTML in Python
6. Cache invalidation and flush
7. Access rights — `check_access` / `has_access` / `_filtered_access`
8. Search by display name — `_search_display_name`
9. `aggregator` instead of `group_operator`
10. Removed/deprecated items
11. Imports and small gotchas
12. Deprecated `record._cr`, `record._context`, `record._uid`
13. `read_group()` deprecated → `_read_group()` / `formatted_read_group()`
14. New `@api.private` decorator
15. `@api.returns` decorator REMOVED
16. New `Domain` API and `any`/`not any` operators
17. `check_access_rights` → `check_access`
18. `env.tz`, `env.company`, `env.companies`

---

### 1. SQL constraints — use `models.Constraint`

Odoo 18 introduced the `Constraint` class as the new declarative API. In Odoo 19 it is the recommended pattern. The legacy `_sql_constraints` list still works but is being phased out.

**Use `models.Constraint(...)` directly — DO NOT import `Constraint` separately.** Just `from odoo import models` is enough.

```python
## ❌ OLD (still works, but legacy)
class Product(models.Model):
    _name = 'product.template'

    _sql_constraints = [
        ('unique_ref', 'UNIQUE(default_code)', 'Product reference must be unique.'),
        ('positive_price', 'CHECK(list_price >= 0)', 'Price must be non-negative.'),
    ]

## ✅ Odoo 19 — preferred. No separate Constraint import.
from odoo import models, fields

class Product(models.Model):
    _name = 'product.template'

    _constraints = [
        models.Constraint('unique_ref', 'UNIQUE(default_code)', 'Product reference must be unique.'),
        models.Constraint('positive_price', 'CHECK(list_price >= 0)', 'Price must be non-negative.'),
    ]
```

```python
## ❌ DON'T do this — extra import is unnecessary in Odoo 19
from odoo.models import Constraint
_constraints = [Constraint(...)]
```

`@api.constrains` decorators for Python-level constraints are unchanged — keep using them as before.

### 2. Display name — `_compute_display_name`

`name_get()` is gone. Override `_compute_display_name` instead. `display_name` is now a proper computed field, so you can `store=True` and use it in search filters / `ORDER BY`.

```python
## ❌ OLD
def name_get(self):
    result = []
    for record in self:
        name = f"{record.name} [{record.color}]" if record.color else record.name
        result.append((record.id, name))
    return result

## ✅ Odoo 19
def _compute_display_name(self):
    for record in self:
        name = f"{record.name} [{record.color}]" if record.color else record.name
        record.display_name = name
```

Inheritance pattern:

```python
## ✅ Odoo 19
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.display_name} (Custom)"
```

### 3. Command objects (replace magic tuples)

Use `Command` for One2many / Many2many writes. The tuple syntax `(0, 0, {...})` still works but is discouraged.

```python
from odoo import Command

## CREATE         old: (0, 0, vals)
Command.create({'name': 'New Line', 'qty': 1})

## UPDATE         old: (1, id, vals)
Command.update(line_id, {'qty': 2})

## DELETE (drop)  old: (2, id, 0)
Command.delete(line_id)

## UNLINK (detach without DB delete)  old: (3, id, 0)
Command.unlink(line_id)

## LINK existing  old: (4, id, 0)
Command.link(line_id)

## CLEAR all      old: (5, 0, 0)
Command.clear()

## SET full list  old: (6, 0, [ids])
Command.set([id1, id2, id3])
```

Real-world example:

```python
## ✅ Odoo 19
from odoo import Command

order = self.env['sale.order'].create({
    'partner_id': partner.id,
    'order_line': [
        Command.create({'product_id': prod1.id, 'product_uom_qty': 2}),
        Command.update(existing_line.id, {'product_uom_qty': 5}),
        Command.delete(old_line.id),
    ],
    'tag_ids': [Command.set([tag1.id, tag2.id])],
})
```

**Import gotcha:**

```python
## ❌ WRONG — ImportError
from odoo.fields import Command

## ✅ CORRECT
from odoo import Command
```

### 4. `_read_group()` API

`read_group()` (returning list of dicts with `[id, display_name]` tuples for relational fields) is replaced by `_read_group()` returning tuples with actual recordsets.

```python
## ❌ OLD
results = self.env['account.move.line'].read_group(
    domain=[('move_id.state', '=', 'posted')],
    fields=['account_id', 'debit:sum', 'credit:sum'],
    groupby=['account_id'],
)
for group in results:
    account_name = group['account_id'][1]   # tuple unpacking
    print(account_name, group['debit'], group['credit'])

## ✅ Odoo 19
results = self.env['account.move.line']._read_group(
    domain=[('move_id.state', '=', 'posted')],
    groupby=['account_id'],
    aggregates=['debit:sum', 'credit:sum'],
)
for account, debit_sum, credit_sum in results:
    print(account.name, debit_sum, credit_sum)   # account is a real record
```

Notes:
- Parameter is `aggregates=` (not `fields=`).
- You can group by date parts (year, month, day, week, hour) numerically in 19.
- You can group/aggregate/order by related no-store fields in 19.

### 5. `Markup()` for HTML in Python (Odoo 17+ still required in 19)

Raw HTML string concatenation is unsafe. All HTML written from Python must use `markupsafe.Markup`. This applies to `message_post`, computed HTML fields, controller responses, etc.

```python
## ❌ OLD — XSS risk
def _get_description(self):
    return "<p>Hello <b>" + self.name + "</b></p>"

## ✅ Odoo 19
from markupsafe import Markup, escape

def _get_description(self):
    return Markup("<p>Hello <b>%s</b></p>") % escape(self.name)
```

`message_post`:

```python
## ✅ Odoo 19
from markupsafe import Markup, escape

self.message_post(
    body=Markup("<p>Invoice <b>%s</b> confirmed</p>") % escape(invoice.name)
)
```

**Pitfall — f-strings inside `Markup()` do NOT escape:**

```python
## ❌ XSS — Markup marks the whole thing safe, including the user input
body = Markup(f"<p>Hello {user_input}</p>")

## ✅ Use % formatting with explicit escape() or rely on % auto-escaping str args
body = Markup("<p>Hello %s</p>") % escape(user_input)
```

### 6. Cache invalidation and flush (granular)

The blanket `flush()` and `invalidate_cache()` are gone. Use the recordset/model-level versions.

```python
## ❌ OLD
self.env['res.partner'].invalidate_cache(['name', 'email'])
self.env['res.partner'].flush()

## ✅ Odoo 19 — recordset level
records.invalidate_recordset(['name', 'email'])
records.flush_recordset(['name', 'email'])

## ✅ Odoo 19 — model level
self.env['res.partner'].invalidate_model(['name'])
self.env['res.partner'].flush_model(['name'])
```

`_flush_search()` is deprecated. Flushing is handled by `execute_query()` based on metadata in the SQL object.

### 7. Access rights — combined methods

Odoo 19 introduces methods that combine access rights AND record rules in a single call:

```python
## ✅ Odoo 19
record.check_access('write')        # raises AccessError if denied
record.has_access('write')           # returns bool
allowed = records._filtered_access('read')   # returns subset accessible to current user
```

Use these instead of the older split `check_access_rights` / `check_access_rule` pattern when you want both checks together.

### 8. Search by display name

`_name_search` is no longer the place to override search-by-name behavior. Implement `_search_display_name` instead, like any other field's search method.

```python
## ✅ Odoo 19
@api.model
def _search_display_name(self, operator, value):
    # custom search logic, returns a domain
    return [('name', operator, value), ('code', operator, value)]
```

### 9. `aggregator` instead of `group_operator`

The `group_operator` parameter on Field is renamed to `aggregator`.

```python
## ❌ OLD
amount = fields.Float(group_operator='avg')

## ✅ Odoo 19
amount = fields.Float(aggregator='avg')
```

### 10. Removed / deprecated items

- `SavepointCase` removed. Use `TransactionCase` (it now handles savepoints automatically when `setUpClass` is defined).
  ```python
  # ✅ Odoo 19
  from odoo.tests import common

  class TestMyModel(common.TransactionCase):
      @classmethod
      def setUpClass(cls):
          super().setUpClass()
          cls.shared = cls.env['my.model'].create({'name': 'X'})
  ```
- `_render_qweb_pdf()` removed. Use `_render()`:
  ```python
  # ✅ Odoo 19
  report = self.env.ref('my_module.action_report_my_doc')
  pdf_content, mime = report._render(self.ids)
  ```
- ORM operator `inselect` removed. Use `in` with a `Query` or `SQL` object.
- `datetime.datetime.utcnow()` is deprecated in Python 3.12. Use `datetime.datetime.now(datetime.timezone.utc)`.
- `distutils` is gone in Python 3.12. Odoo 19 requires Python 3.11+.

### 11. Imports and small gotchas

- `from odoo import Command` — not `odoo.fields`.
- For `Constraint`, just use `models.Constraint(...)` after `from odoo import models`. No separate import needed.
- `from markupsafe import Markup, escape` for HTML.
- `from odoo.osv.expression import OR` is **deprecated** in Odoo 19. Use `Domain.OR` (see section 16).
- `odoo.osv` module is deprecated overall — prefer `odoo.Domain` API and `odoo.fields` for field types.
- Many model names changed in Odoo 19 — always check `model_renames.md` before referencing a model by string.

### 12. Deprecated `record._cr`, `record._context`, `record._uid`

The shortcut attributes on records are deprecated in Odoo 19. Use `record.env.*` instead.

```python
## ❌ OLD / deprecated in Odoo 19
self._cr.execute("SELECT ...")
ctx = self._context
uid = self._uid

## ✅ Odoo 19
self.env.cr.execute("SELECT ...")
ctx = self.env.context
uid = self.env.uid
```

This applies in any model method, controller, or wizard. The deprecation also extends to `self._context` patterns commonly used to read context flags.

### 13. `read_group()` deprecated → `_read_group()` or `formatted_read_group()`

The public `read_group()` method is deprecated in Odoo 19. Two replacements depending on the use case:

- **`_read_group()`** — for **backend / Python** usage (returns tuples with real recordsets, see section 4).
- **`formatted_read_group()`** — formatted public API, for cases where you previously needed `read_group`'s dict format.

```python
## ❌ OLD — deprecated in 19
results = self.env['account.move.line'].read_group(
    domain=[('state', '=', 'posted')],
    fields=['account_id', 'debit:sum'],
    groupby=['account_id'],
)

## ✅ Odoo 19 — backend usage (preferred)
results = self.env['account.move.line']._read_group(
    domain=[('state', '=', 'posted')],
    groupby=['account_id'],
    aggregates=['debit:sum'],
)
for account, debit_sum in results:
    ...

## ✅ Odoo 19 — public/formatted API
results = self.env['account.move.line'].formatted_read_group(
    domain=[('state', '=', 'posted')],
    groupby=['account_id'],
    aggregates=['debit:sum'],
)
```

### 14. New `@api.private` decorator

Odoo 19 introduces `@api.private` to mark Python methods as **not** exposed via RPC. This is a security feature: by default Odoo allows RPC clients to call any public model method; `@api.private` opts a method out.

```python
from odoo import api, models

class MyModel(models.Model):
    _name = 'my.model'

    @api.private
    def _internal_helper(self):
        """Cannot be called via XML-RPC / JSON-RPC by external clients."""
        ...

    def public_method(self):
        """Still callable via RPC by default."""
        ...
```

Use `@api.private` for any helper method that should run only inside server code. Method names starting with `_` already have a soft convention of being private, but `@api.private` makes it enforced.

### 15. `@api.returns` decorator REMOVED

`@api.returns(...)` is removed in Odoo 19. Use modern API patterns — return recordsets directly, or use type hints if needed for clarity.

```python
## ❌ OLD — ImportError or no-op in Odoo 19
@api.returns('res.partner', lambda value: value.id)
def my_method(self):
    return self.env['res.partner'].browse(...)

## ✅ Odoo 19 — just return the recordset
def my_method(self):
    return self.env['res.partner'].browse(...)
```

### 16. New domain API — `Domain` class and `any`/`not any` operators

Odoo 19 introduces a proper `Domain` class (`odoo.Domain`) replacing the older `osv.expression` helpers, plus new domain operators for relational traversal.

#### `Domain.OR` / `Domain.AND` replace `expression.OR` / `expression.AND`

```python
## ❌ OLD / deprecated in Odoo 19
from odoo.osv.expression import OR, AND
combined = OR([domain_a, domain_b])

## ✅ Odoo 19
from odoo import Domain
combined = Domain.OR([domain_a, domain_b])
## or:
combined = Domain.AND([domain_a, domain_b])
```

#### `any` / `not any` operators for relational fields

For querying related models in a domain (instead of dot-notation traversal), Odoo 19 supports `any` and `not any`:

```python
## ✅ Odoo 19
## "find partners that have any sale order in state 'sale'"
domain = [('sale_order_ids', 'any', [('state', '=', 'sale')])]

## "find partners with NO sale order in 'cancel' state"
domain = [('sale_order_ids', 'not any', [('state', '=', 'cancel')])]
```

There are also **internal-only** operators `any!` and `not any!` that bypass access rights and record rules. **NEVER use `any!`/`not any!` in domains coming from RPC/user input** — they're for trusted server-side logic only (computed fields, cron jobs, internal queries).

```python
## ✅ Odoo 19 — server-side only, bypasses access rights
domain = [('document_ids', 'any!', [('confidential', '=', True)])]
```

#### Domain operators must be lowercase

Since 19.0, uppercase operators raise a deprecation warning. Always lowercase:

```python
## ❌ Triggers DeprecationWarning in 19
[('name', 'LIKE', 'foo')]
[('state', 'IN', ['draft', 'sent'])]

## ✅ Odoo 19
[('name', 'like', 'foo')]
[('state', 'in', ['draft', 'sent'])]
```

#### Custom SQL in domains via `Domain.custom`

For injecting custom SQL into a domain (replacing legacy patterns that subclassed expression):

```python
## ✅ Odoo 19
from odoo import Domain
from odoo.tools import SQL

domain = Domain.custom(to_sql=lambda model, alias, query: SQL("...custom condition..."))
```

### 17. `check_access_rights` → `check_access`

The split methods are merged. Use `check_access` (raises) or `has_access` (bool) — see section 7 for details.

```python
## ❌ OLD
record.check_access_rights('write')
record.check_access_rule('write')

## ✅ Odoo 19 — combined
record.check_access('write')          # raises
record.has_access('write')            # bool
```

### 18. `env.tz`, `env.company`, `env.companies` — modern context APIs

Odoo 19 standardizes a few env-level helpers:

- **`env.tz`** — current timezone (string), replaces old `self._context.get('tz')` patterns.
- **`env.company`** — the active company recordset (single).
- **`env.companies`** — companies the user is currently allowed to operate in (recordset).

```python
## ❌ OLD
tz = self._context.get('tz') or self.env.user.tz
allowed_companies = self.env.context.get('allowed_company_ids', [])

## ✅ Odoo 19
tz = self.env.tz
active_company = self.env.company
allowed_companies = self.env.companies
```

For multi-company filtering, prefer `env.companies` over manual context inspection.

---

## XML Views (form, list, kanban, search)

## Odoo 19 — XML Views Reference

This reference covers all XML view changes: form, list (formerly tree), kanban, search, QWeb templates, chatter.

### Table of contents
1. `attrs` and `states` — fully removed, use inline expressions
2. `<tree>` → `<list>`
3. Kanban templates — `kanban-card` → `card`
4. `t-raw` removed, `t-esc` removed, `t-call` new syntax — use `t-out`
5. Chatter shorthand `<chatter/>`
6. `column_invisible` syntax
7. XPath updates for inherited views
8. Search view — `<group>` cannot have `string` or `expand`
9. Complete migrated form view example

---

### 1. `attrs` and `states` — fully removed (gone since Odoo 17)

The `attrs="{...}"` dict-in-XML pattern was removed in Odoo 17 and stays removed in 18, 19. Same for the `states="..."` shorthand on buttons/fields. Use inline boolean expressions on `invisible`, `readonly`, `required`, `column_invisible`.

```xml
<!-- ❌ OLD -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly':  [('state', 'not in', ['draft', 'sent'])],
               'required':  [('state', '=', 'confirmed')]}" />

<button name="action_confirm"
        states="draft"
        type="object" string="Confirm"/>

<!-- ✅ Odoo 19 -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state not in ('draft', 'sent')"
       required="state == 'confirmed'" />

<button name="action_confirm"
        invisible="state != 'draft'"
        type="object" string="Confirm"/>
```

#### Expression syntax cheat-sheet

```xml
<!-- equality -->
<field name="x" invisible="state == 'draft'"/>

<!-- not equal -->
<field name="x" invisible="state != 'sale'"/>

<!-- in / not in -->
<field name="x" invisible="state in ('draft', 'cancel')"/>
<field name="x" invisible="state not in ('sale', 'done')"/>

<!-- boolean -->
<field name="x" invisible="not active"/>
<field name="x" invisible="active"/>

<!-- AND -->
<field name="x" invisible="state == 'draft' and type == 'service'"/>

<!-- OR -->
<field name="x" invisible="type == 'service' or not active"/>

<!-- numeric -->
<field name="x" readonly="qty_invoiced &gt; 0"/>
<!-- (use &gt; / &lt; in XML, or wrap in CDATA) -->

<!-- nested -->
<field name="x" invisible="(state == 'draft' and not partner_id) or state == 'cancel'"/>
```

These expressions evaluate in a JavaScript-like context: no Python imports, no function calls, just comparisons and logical operators. For complex logic, add a Boolean computed field on the model.

#### Pitfall: inverted `states`

`states="draft"` meant **visible when state is draft**. The inline equivalent is `invisible="state != 'draft'"`. `states="draft,sent"` → `invisible="state not in ('draft', 'sent')"`. Drop a `not` and the element vanishes.

### 2. `<tree>` → `<list>`

Tree views are now list views. Rename the tag everywhere — view definition AND inherited XPath targets.

```xml
<!-- ❌ OLD -->
<tree string="Sale Orders" decoration-danger="state == 'cancel'">
    <field name="name"/>
    <field name="state"/>
</tree>

<!-- ✅ Odoo 19 -->
<list string="Sale Orders" decoration-danger="state == 'cancel'">
    <field name="name"/>
    <field name="state"/>
</list>
```

Inherited views:

```xml
<!-- ❌ OLD XPath -->
<xpath expr="//field[@name='order_line']/tree/field[@name='price_unit']" position="after">

<!-- ✅ Odoo 19 -->
<xpath expr="//field[@name='order_line']/list/field[@name='price_unit']" position="after">
```

The view type in `ir.actions.act_window` records is also `list` (not `tree`):

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="view_mode">list,form</field>   <!-- not "tree,form" -->
</record>
```

### 3. Kanban templates — `kanban-card` → `card`

The kanban template name changed and the structure was simplified. Use `<header>`, `<main>`, `<footer>` semantic blocks instead of nested divs.

```xml
<!-- ❌ OLD -->
<kanban>
    <templates>
        <t t-name="kanban-card">
            <div class="oe_kanban_card oe_kanban_global_click">
                <div class="o_kanban_record_top">
                    <strong><field name="name"/></strong>
                </div>
                <div class="o_kanban_record_bottom">
                    <field name="priority" widget="priority"/>
                    <field name="user_id" widget="many2one_avatar_user"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>

<!-- ✅ Odoo 19 -->
<kanban>
    <templates>
        <t t-name="card">
            <field name="name" class="fw-bold"/>
            <footer>
                <field name="priority" widget="priority"/>
                <field name="user_id" widget="many2one_avatar_user" class="ms-auto"/>
            </footer>
        </t>
    </templates>
</kanban>
```

### 4. `t-raw` removed, `t-esc` removed → use `t-out`

`t-raw` was removed in Odoo 17 (XSS risk). `t-esc` was deprecated in 17/18 and is **fully removed in Odoo 19** — using it raises a template error. The single replacement for both is `t-out`, which auto-escapes plain strings and renders `Markup()` objects as HTML.

```xml
<!-- ❌ OLD / fails in Odoo 19 -->
<div t-raw="record.description"/>
<span t-esc="record.name"/>

<!-- ✅ Odoo 19 — t-out for everything -->
<div t-out="record.description"/>
<span t-out="record.name"/>
```

If you genuinely need to render raw HTML from a controlled Python source, return a `Markup()` object from Python — `t-out` will render it as HTML. Plain strings always get escaped.

#### `t-call` new attribute syntax

Odoo 19 prefers attribute-based parameter passing for `t-call`, replacing the older `t-set` block approach. Both still work for now, but the new form is cleaner and the documented standard going forward.

```xml
<!-- ❌ OLD (still works, but messier) -->
<t t-call="my_module.my_template">
    <t t-set="custom_value" t-value="x + y"/>
    <t t-set="title" t-value="'Hello'"/>
</t>

<!-- ✅ Odoo 19 — preferred -->
<t t-call="my_module.my_template" custom_value="x + y" title="'Hello'"/>
```

Inside the called template, the values are accessed the same way (as variables in the rendering context).

### 5. Chatter shorthand `<chatter/>`

Replace the verbose three-field chatter boilerplate with `<chatter/>`.

```xml
<!-- ❌ OLD -->
<div class="oe_chatter">
    <field name="message_follower_ids" widget="mail_followers"/>
    <field name="activity_ids" widget="mail_activity"/>
    <field name="message_ids" widget="mail_thread"/>
</div>

<!-- ✅ Odoo 19 -->
<chatter/>
```

### 6. `column_invisible` syntax inside O2M sub-views

When you want a column hidden inside an embedded list view based on the parent record's state, use `column_invisible` with the `parent.` prefix in an inline expression:

```xml
<!-- ✅ Odoo 19 -->
<field name="order_line">
    <list editable="bottom">
        <field name="product_id"/>
        <field name="qty_delivered"
               column_invisible="parent.state == 'draft'"/>
    </list>
</field>
```

### 7. XPath updates for inherited views

When inheriting from core views or your own older views, audit every XPath:
- `tree` → `list` (in expressions targeting the tag).
- Avoid targeting `attrs` attributes — they no longer exist; target the new inline attributes (`invisible`, `readonly`, `required`).
- Avoid targeting the old chatter divs if the parent moved to `<chatter/>`.

### 8. Search view — `<group>` cannot have `string` or `expand` attributes

In Odoo 19 search views, the `<group>` element used to wrap "Group By" filters does NOT accept `string` OR `expand` attributes. Both `<group string="Group By">` and `<group expand="0">` patterns from older versions are removed. Leave the tag bare.

```xml
<!-- ❌ OLD / breaks in Odoo 19 -->
<search>
    <field name="name"/>
    <filter name="my_filter" string="Mine" domain="[('user_id', '=', uid)]"/>
    <group expand="0" string="Group By">
        <filter name="group_by_state" string="State" context="{'group_by': 'state'}"/>
        <filter name="group_by_user" string="User" context="{'group_by': 'user_id'}"/>
    </group>
</search>

<!-- ✅ Odoo 19 — bare <group>, no string, no expand -->
<search>
    <field name="name"/>
    <filter name="my_filter" string="Mine" domain="[('user_id', '=', uid)]"/>
    <group>
        <filter name="group_by_state" string="State" context="{'group_by': 'state'}"/>
        <filter name="group_by_user" string="User" context="{'group_by': 'user_id'}"/>
    </group>
</search>
```

The "Group By" label is provided by the framework automatically. Both attributes were legacy holdovers.

This rule is **specific to search views**. In form views and other contexts, `<group string="...">` is still valid and renders as a section header.

### 9. Complete migrated form view

```xml
<!-- ✅ Odoo 19 form view, fully migrated -->
<form string="Sale Order">
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                invisible="state != 'draft'"/>
        <button name="action_cancel" type="object" string="Cancel"
                invisible="state in ('cancel', 'done')"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,sale,done"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name" readonly="state != 'draft'"/></h1>
        </div>
        <group>
            <group>
                <field name="partner_id"
                       readonly="state not in ('draft', 'sent')"/>
                <field name="date_order"
                       required="state == 'sale'"/>
            </group>
            <group>
                <field name="warehouse_id"
                       invisible="picking_policy == 'direct'"/>
            </group>
        </group>
        <notebook>
            <page string="Order Lines">
                <field name="order_line"
                       readonly="state in ('done', 'cancel')">
                    <list editable="bottom">
                        <field name="product_id"/>
                        <field name="qty_delivered"
                               column_invisible="parent.state == 'draft'"/>
                    </list>
                </field>
            </page>
        </notebook>
    </sheet>
    <chatter/>
</form>
```

---

## HTTP Controllers

## Odoo 19 — Controllers Reference

This reference covers HTTP controllers, route types, and authentication.

### Table of contents
1. `type="json"` → `type="jsonrpc"` for web-client RPC
2. `auth="bearer"` for API tokens
3. Three route types — when to use each
4. Common pitfalls

---

### 1. `type="json"` vs `type="jsonrpc"`

Odoo 17 split JSON endpoints into two types and renamed the JSON-RPC variant. Odoo 19 keeps this distinction. The Odoo web client (calls from JS via `rpc` service) uses **JSON-RPC 2.0** — endpoints called by the web client must declare `type="jsonrpc"`.

```python
## ❌ OLD — works for plain JSON only, web client RPC will fail
@http.route('/my_module/get_data', type='json', auth='user')
def get_data(self, **kwargs):
    return {'data': request.env['my.model'].search([]).read(['name'])}

## ✅ Odoo 19 — for endpoints called by the Odoo web client (JS rpc service)
@http.route('/my_module/get_data', type='jsonrpc', auth='user')
def get_data(self, **kwargs):
    return {'data': request.env['my.model'].search([]).read(['name'])}
```

The Python signature and return shape are identical — only the `type` parameter changes. The same names are still imported the same way:

```python
from odoo import http
from odoo.http import request
```

### 2. `auth="bearer"` for API tokens

For external API consumers using bearer tokens (e.g., third-party integrations), use `auth="bearer"`:

```python
## ✅ Odoo 19
@http.route('/api/v1/resource', auth='bearer', type='jsonrpc')
def api_resource(self):
    return {'user': request.env.user.name}
```

The token is sent as `Authorization: Bearer <token>` header. Configure tokens via `res.users.apikeys` (UI: Developer Mode → user form → API Keys).

### 3. The three route types — when to use each

| `type` | When to use |
|---|---|
| `http` | Plain HTTP endpoints returning HTML, files, redirects. Public pages, file downloads. |
| `jsonrpc` | Endpoints called by the Odoo web client via the `rpc` service. JSON-RPC 2.0 protocol. |
| `json` | Plain JSON request/response (POST with JSON body, get JSON back) — for non-Odoo callers that don't speak JSON-RPC. |

Examples:

```python
## Public web page
@http.route('/about', type='http', auth='public', website=True)
def about(self):
    return request.render('my_module.about_page')

## Web-client RPC (called from OWL with rpc('/my_module/data', {...}))
@http.route('/my_module/data', type='jsonrpc', auth='user')
def data(self, **kw):
    return {'records': [...]}

## REST-ish JSON for an external integration
@http.route('/api/v1/orders', type='json', auth='bearer', methods=['POST'], csrf=False)
def create_order(self, **payload):
    order = request.env['sale.order'].create(payload)
    return {'id': order.id}
```

### 4. Common pitfalls

#### The Phantom JSON Endpoint
Forgetting `type="json"` → `type="jsonrpc"` for endpoints called by the Odoo web client. Symptom: silent failure, cryptic 404s, JSON parsing errors in browser console. Always check whether the caller is the web client (use `jsonrpc`) or an external system (use `json`).

#### CSRF on POST endpoints
Public POST endpoints called by external systems need `csrf=False`. Endpoints called by the web client get the CSRF token automatically.

#### Auth modes
- `auth='public'` — anyone, no login. Use sparingly.
- `auth='user'` — must be logged in.
- `auth='bearer'` — API token (Odoo 17+).
- `auth='none'` — no env, raw request. Almost never what you want.

#### `request` import
Import is unchanged: `from odoo.http import request`. Inside controllers, `request.env` gives you the environment, `request.httprequest` is the WSGI/Werkzeug request.

---

## OWL Components & JavaScript

## Odoo 19 — OWL & JavaScript Reference

This reference covers OWL 2 components, services, and the modern JS architecture used in `static/src/`. Odoo 17 finalized the move to OWL 2 and the new JS service layer; Odoo 19 continues those conventions.

### Table of contents
1. OWL 2 component basics
2. Frozen `env` — use `useSubEnv`
3. No more `t-ref` to child components
4. No `class`/`style` auto-forwarding to root element
5. `t-on` callbacks → prefer prop callbacks
6. Patching components (`patch` from `@web/core/utils/patch`)
7. RPC calls — use the `rpc` service
8. Services and `useService`
9. Registry and component registration
10. Removed jQuery & legacy widgets
11. CSP — no inline scripts, no CDN injection
12. POS — `get_order()` → `getOrder()` (camelCase rename)
13. New `useSortable` hook
14. Website / eCommerce — `request.cart` and `request.pricelist`

---

### 1. OWL 2 component basics

An Odoo 19 OWL component is a class with a `static template` reference and lifecycle hooks via the `setup()` method.

```javascript
/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyWidget extends Component {
    static template = "my_module.MyWidget";
    static props = {
        record: { type: Object, optional: true },
    };

    setup() {
        this.state = useState({ count: 0 });
        onMounted(() => console.log("mounted"));
    }

    increment() {
        this.state.count++;
    }
}

registry.category("fields").add("my_widget", { component: MyWidget });
```

Key points for OWL 2:
- Components extend `Component` from `@odoo/owl`.
- `setup()` replaces constructor logic and is where hooks (`useState`, `useService`, `useRef`, etc.) are called.
- `static template` is a string reference to a QWeb template name.
- `static props` declares accepted props (validated at runtime in dev).

### 2. Frozen `env` — use `useSubEnv` to extend it

In OWL 2, `env` is frozen and cannot be mutated. To pass data to descendant components, use `useSubEnv` (from `@odoo/owl`):

```javascript
// ❌ OLD (OWL 1)
this.env.myValue = 42;

// ✅ Odoo 19 (OWL 2)
import { Component, useSubEnv } from "@odoo/owl";

export class Parent extends Component {
    setup() {
        useSubEnv({ myValue: 42 });
    }
}
```

Children read it as `this.env.myValue`.

### 3. No more `t-ref` to child components

In OWL 1, `t-ref` could grab a reference to a child component instance. In OWL 2 it only refs DOM elements.

```xml
<!-- ❌ OLD — gets child component instance in OWL 1, doesn't work in 2 -->
<MyChild t-ref="child"/>

<!-- ✅ Odoo 19 — t-ref only refs HTML elements -->
<div t-ref="myDiv"/>
```

```javascript
import { Component, useRef } from "@odoo/owl";

export class Parent extends Component {
    setup() {
        this.myDiv = useRef("myDiv");   // refs the <div>, not a component
    }
}
```

To communicate with children, pass props (including callbacks) and let children call back up.

### 4. No `class`/`style` auto-forwarding to root element

In OWL 1, putting `class="..."` on a `<MyChild>` tag would forward to the child's root DOM. In OWL 2 these are now plain props — the child must explicitly use them in its template.

```xml
<!-- Parent -->
<MyChild class="'extra-class'" style="'color: red'"/>
<!-- Note: must be JS expression, hence the string quotes -->

<!-- Child template — must explicitly apply -->
<div t-att-class="props.class" t-att-style="props.style">
    ...
</div>
```

### 5. `t-on` callbacks — prefer prop callbacks

For parent ↔ child communication, OWL 2 favors callback props over `t-on` event listeners.

```javascript
// Parent passes a callback
export class Parent extends Component {
    static template = "Parent";
    onChildClick(value) {
        console.log("child said", value);
    }
}
```

```xml
<!-- Parent template -->
<MyChild onClick.bind="onChildClick"/>
```

```javascript
// Child invokes the callback
export class MyChild extends Component {
    static template = "MyChild";
    static props = { onClick: Function };
    handle() {
        this.props.onClick("hello");
    }
}
```

`t-on:click` is still valid for binding to native DOM events on actual HTML elements inside a template.

### 6. Patching components

To patch an existing OWL component (instead of overriding via class extension), use the `patch` utility:

```javascript
/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup();
        // additional setup
    },

    async saveRecord(...args) {
        console.log("saving");
        return super.saveRecord(...args);
    },
});
```

Notes:
- Use `super.method(...)` to call the original.
- `patch` mutates the prototype; use it sparingly for core components.
- The third argument (legacy `{...}` options object) is removed in modern Odoo — just pass two args: target and patch object.

### 7. RPC calls — `rpc` service

Don't use raw `fetch` for Odoo backend calls. Use the `rpc` service:

```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    setup() {
        this.rpc = useService("rpc");
    }

    async loadData() {
        const result = await this.rpc("/my_module/get_data", {
            ids: [1, 2, 3],
        });
        return result;
    }
}
```

The matching Python controller should use `type='jsonrpc'` (see `controllers.md`).

For ORM calls, use the `orm` service:

```javascript
this.orm = useService("orm");
const records = await this.orm.searchRead("res.partner", [["is_company", "=", true]], ["name", "email"]);
```

### 8. Services and `useService`

Common services (request via `useService("name")`):
- `"rpc"` — JSON-RPC calls to controllers.
- `"orm"` — ORM operations (search, read, create, write, unlink, call).
- `"notification"` — show toast notifications.
- `"dialog"` — open a dialog.
- `"action"` — execute Odoo actions (open form, run server action).
- `"user"` — current user info, has_group, etc.
- `"router"` — URL/state.

```javascript
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MyView extends Component {
    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
    }
    notify() {
        this.notification.add("Saved!", { type: "success" });
    }
    openPartners() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            views: [[false, "list"], [false, "form"]],
        });
    }
}
```

### 9. Registry and component registration

Register custom widgets, fields, services via the central `registry`:

```javascript
import { registry } from "@web/core/registry";

// Register a field widget
registry.category("fields").add("my_widget", { component: MyWidget });

// Register a service
registry.category("services").add("myService", {
    dependencies: ["rpc"],
    start(env, { rpc }) {
        return { doThing: () => rpc("/my/route", {}) };
    },
});

// Register a view (uncommon)
registry.category("views").add("my_view", { ... });
```

Common categories: `fields`, `services`, `views`, `actions`, `main_components`, `systray`.

### 10. No more jQuery or legacy widgets

- No `$.fn.myPlugin(...)` — jQuery is no longer included by default (Odoo 17+).
- The `web.Widget` legacy class is gone in Odoo 19. All UI is OWL.
- The `core.bus` event bus pattern is replaced by services and reactive state.

### 11. CSP — no inline scripts, no CDN injection

Odoo 18+ enforces strict Content Security Policy. Two patterns that BREAK:

```javascript
// ❌ BREAKS — CSP blocks inline script creation with external src
const s = document.createElement("script");
s.src = "https://cdn.example.com/lib.js";
document.head.appendChild(s);
```

```xml
<!-- ❌ BREAKS — no inline <script> in QWeb -->
<t t-name="MyTemplate">
    <script>console.log("hi");</script>
</t>
```

Vendor third-party libraries into your module's `static/lib/` and declare them in the asset bundle:

```python
## __manifest__.py
{
    'assets': {
        'web.assets_backend': [
            'my_module/static/lib/some-library/some-library.min.js',
            'my_module/static/src/js/my_component.js',
            'my_module/static/src/xml/my_template.xml',
        ],
    },
}
```

QWeb templates are loaded from XML files declared in the same asset bundle.

### 12. POS — `get_order()` → `getOrder()` (camelCase rename)

Point of Sale's JS API moved its order-access method to camelCase to match the rest of the JS codebase:

```javascript
// ❌ OLD
const order = this.pos.get_order();

// ✅ Odoo 19
const order = this.pos.getOrder();
```

This is part of a broader naming consistency effort in the POS module. If you patch or extend POS components, audit all `pos.snake_case_method()` calls — many have been or will be renamed to `camelCase`. The Odoo POS frontend is the most affected area.

### 13. New `useSortable` hook

Odoo 19 ships a `useSortable` hook for drag-and-drop ordering of records, useful for kanban-style or list reordering:

```javascript
import { Component, useRef } from "@odoo/owl";
import { useSortable } from "@web/core/utils/sortable_owl";

export class MyList extends Component {
    setup() {
        this.listRef = useRef("list");
        useSortable({
            ref: this.listRef,
            elements: ".sortable-item",
            onDrop: ({ element, previous, next }) => {
                // reorder logic
            },
        });
    }
}
```

### 14. Website / eCommerce — `request.cart` and `request.pricelist`

For modules that touched the website-sale flow:

```python
## ❌ OLD
order = request.website.sale_get_order()
pricelist = request.website.pricelist_id

## ✅ Odoo 19
order = request.cart                  # current cart for this request
pricelist = request.pricelist         # current pricelist
## To create a fresh cart:
new_cart = request.website._create_cart()
```

This makes the cart lifecycle explicit and tied to the HTTP request rather than implicit on the website model.

---

## Manifest, Hooks & Security

## Odoo 19 — Manifest, Hooks & Security Reference

This reference covers `__manifest__.py`, install/upgrade hooks, asset bundles, and security file conventions.

### Table of contents
1. `__manifest__.py` shape
2. `license` field is mandatory
3. `version` field — must start with `19.0`
4. Asset bundles — vendor libs and QWeb templates
5. Hook signatures (`post_init_hook`, etc.)
6. Security — `ir.model.access.csv` and `ir.rule`
7. The `res.groups` privilege refactor (Odoo 19)
8. `groups_id` → `group_ids` rename
9. Python version and dependencies
10. Server config — `xmlrpc_port` → `http_port`
11. Demo data not loaded by default

---

### 1. `__manifest__.py` shape

A minimal Odoo 19 manifest:

```python
{
    'name': 'My Module',
    'summary': 'Short one-line summary',
    'description': 'Longer description.',
    'author': 'Your Name',
    'website': 'https://example.com',
    'category': 'Sales',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',                         # MANDATORY
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/my_model_views.xml',
        'data/data.xml',
    ],
    'demo': ['demo/demo.xml'],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/my_component.js',
            'my_module/static/src/xml/my_component.xml',
            'my_module/static/src/scss/my_component.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
```

### 2. `license` is mandatory

Since Odoo 17, omitting `'license'` raises an error on install. Common values:
- `'LGPL-3'` (most permissive for proprietary use)
- `'AGPL-3'`
- `'OPL-1'` (Odoo Proprietary License — for paid modules)
- `'Other proprietary'`

### 3. `version` field

Must start with `19.0` for an Odoo 19 module. Convention: `'19.0.MAJOR.MINOR.PATCH'` — e.g., `'19.0.1.0.0'`.

If you skip the `19.0.` prefix and write just `'1.0.0'`, Odoo prepends its own version, which can cause unexpected upgrade-script execution.

### 4. Asset bundles

Asset declaration uses the `assets` dict in the manifest. Common bundles:

| Bundle | When loaded |
|---|---|
| `web.assets_backend` | Backend (logged-in app) |
| `web.assets_frontend` | Public website |
| `web.assets_common` | Both |
| `web.assets_tests` | Test runner |
| `web.assets_qweb` | (legacy, avoid) |

QWeb templates for OWL components are XML files included in the same bundle as the JS that uses them — they don't need a separate registration step.

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/scss/styles.scss',
        'my_module/static/src/js/my_widget.js',
        'my_module/static/src/xml/my_widget.xml',   # OWL templates
        'my_module/static/lib/lodash/lodash.min.js',  # vendored 3rd-party
    ],
},
```

To prepend, append, replace, or remove items in inherited bundles, use tuple operations:

```python
'assets': {
    'web.assets_backend': [
        ('after', 'web/static/src/core/foo.js', 'my_module/static/src/js/foo_patch.js'),
        ('replace', 'other/static/src/something.js', 'my_module/static/src/js/replacement.js'),
        ('remove', 'web/static/src/legacy/legacy.js'),
    ],
},
```

### 5. Hook signatures

Install/upgrade/uninstall hooks now receive `env` directly (Odoo 17+). The old `(cr, registry)` signature is gone.

```python
## ❌ OLD
def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['my.model'].search([])._do_something()

## ✅ Odoo 19
def post_init_hook(env):
    env['my.model'].search([])._do_something()
```

Same signature change for `pre_init_hook`, `uninstall_hook`, `post_load`. Refer to them by string in the manifest:

```python
{
    ...
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

The functions themselves typically live in the module's `__init__.py` or `hooks.py`.

### 6. Security — `ir.model.access.csv`

Standard CSV format (unchanged in 19):

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
```

Record rules in `ir.rule` use `domain_force` — domains in record rules are unchanged syntactically, but if your domain references the renamed user-group field on `res.users`, see section 8.

### 7. The `res.groups` privilege refactor (NEW in Odoo 19)

Odoo 19 introduces `res.groups.privilege` — a model that groups related security groups for cleaner privilege management.

```python
## Old: groups had categories via res.groups.category_id (a M2O to ir.module.category)
## Odoo 19: res.groups now has privilege_id (M2O to res.groups.privilege)
```

If you previously did:

```python
self.env['res.groups'].search([('category_id.name', '=', 'Sales')])
```

In Odoo 19 the equivalent is via privilege:

```python
self.env['res.groups'].search([('privilege_id.name', '=', 'Sales')])
```

The `ir.module.category` table itself still exists and is still used for module categorization in the apps menu — it's the link from groups to it that changed.

### 8. `groups_id` → `group_ids` rename

The user → groups relation field is renamed, and this cascades across many places:

| Old | Odoo 19 |
|---|---|
| `res.users.groups_id` | `res.users.group_ids` |
| `res.groups.users` | `res.groups.user_ids` |

This affects:
- Domains and search calls referencing the field on `res.users` or `res.groups`.
- `ir.actions.act_window.groups_id` (action visibility) — same rename.
- `ir.actions.server.groups_id` — same.
- `ir.actions.report.groups_id` — same.
- `ir.ui.view.groups_id` — same.
- `ir.ui.menu.groups_id` — same.

```python
## ❌ OLD code that breaks in 19
user.groups_id |= self.env.ref('sale.group_sale_manager')

## ✅ Odoo 19
user.group_ids |= self.env.ref('sale.group_sale_manager')

## In domains:
## ❌  ('groups_id', 'in', [...])
## ✅  ('group_ids', 'in', [...])
```

Record rules with `domain_force` referencing these fields need to be updated too.

### 9. Python version and dependencies

- **Python 3.10 minimum** for Odoo 19 (recommended: 3.12 for best performance).
- `datetime.utcnow()` is deprecated — use `datetime.now(datetime.timezone.utc)`.
- `distutils` is gone in Python 3.12 — use `packaging` or `setuptools` alternatives.
- `external_dependencies` in the manifest declares Python and binary requirements:

```python
'external_dependencies': {
    'python': ['pandas', 'requests'],
    'bin': ['wkhtmltopdf'],
},
```

### 10. Server config — `xmlrpc_port` → `http_port`

The Odoo server config file (`odoo.conf`) renamed the HTTP port option:

```ini
; ❌ OLD (Odoo 18 and earlier)
[options]
xmlrpc_port = 8069

; ✅ Odoo 19
[options]
http_port = 8069
```

This drops the legacy XML-RPC reference in favor of a cleaner name. Same applies to `xmlrpc_interface` → `http_interface`. If you have deployment scripts, Docker compose, or systemd unit files that pass these options via `--xmlrpc-port`, switch to `--http-port` for Odoo 19.

### 11. Demo data not loaded by default

Odoo 19 changed the default: demo data is **no longer loaded automatically** when creating a new database. Pass `--without-demo=False` (or set explicitly in config) if you actually want demo data. For tests, this means tests that previously relied on demo records present "by accident" must declare those records explicitly via test data files or `setUp`.

---

## SCSS & Assets

## Odoo 19 — SCSS & Assets Reference

This reference covers SCSS/Sass migration for the dart-sass compiler (Odoo 17 introduced it, Odoo 18 enforces it, Odoo 19 stays on it).

### Table of contents
1. Division operator — `/` no longer divides
2. `@import` is dead — use `@use` / `@forward`
3. Module-namespaced variables and mixins
4. Asset registration (recap)
5. CSS custom properties

---

### 1. Division operator

In dart-sass, `/` is treated as the CSS slash separator (e.g., `font: 16px/1.5 Arial`), NOT division. For arithmetic, use `math.div()` or `calc()`.

```scss
// ❌ OLD (libsass — Odoo 16) — division worked
.element {
    width: 100px / 2;        // = 50px in libsass, literal "100px / 2" in dart-sass
    font-size: 24px / 1.5;
}

// ✅ Odoo 19 — explicit math.div
@use "sass:math";

.element {
    width: math.div(100px, 2);
    font-size: math.div(24px, 1.5);
}

// ✅ Or use CSS calc() — works in any version
.element {
    width: calc(100px / 2);
    font-size: calc(24px / 1.5);
}
```

### 2. `@import` is dead — use `@use` / `@forward`

Sass `@import` is deprecated in dart-sass and will be removed. Odoo 18+ refuses or warns aggressively. Replace with `@use` and `@forward`.

```scss
// ❌ OLD
@import "variables";
@import "mixins";

.element {
    color: $primary-color;
    @include my-mixin();
}

// ✅ Odoo 19 — namespaced
@use "variables" as vars;
@use "mixins" as mix;

.element {
    color: vars.$primary-color;
    @include mix.my-mixin();
}

// ✅ Odoo 19 — wildcard namespace (closest to old behavior)
@use "variables" as *;
@use "mixins" as *;

.element {
    color: $primary-color;
    @include my-mixin();
}
```

`@forward` is for re-exporting from index/barrel files:

```scss
// _index.scss
@forward "variables";
@forward "mixins";
@forward "components";

// In a consuming file
@use "index" as *;
```

### 3. Module-namespaced variables and mixins

Differences when using `@use` (vs `@import`):
- Variables, mixins, and functions are namespaced by default — refer to them as `namespace.$var`, `namespace.mix($args)`.
- Use `as *` to import unprefixed (less safe, but matches old `@import` behavior).
- Use `as alias` for a custom prefix.
- Each `@use` is loaded once per file; `@import` could be repeated.
- Private members (prefixed with `_` or `-`) are not accessible across modules.

```scss
// _utils.scss
$primary: #875A7B;
$_secret: #000;        // private, not accessible from other files

@function double($x) { @return $x * 2; }

// _component.scss
@use "utils";

.box {
    color: utils.$primary;        // ✅
    width: utils.double(10px);    // ✅
    // background: utils.$_secret; // ❌ ERROR — private
}
```

### 4. Asset registration (recap)

SCSS files are added to bundles in `__manifest__.py` like any other asset:

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/scss/_variables.scss',
        'my_module/static/src/scss/main.scss',
    ],
},
```

Order matters when files use `@use` of relative paths. List shared/dependency files before files that consume them.

### 5. CSS custom properties

Native CSS variables (`--name: value;`) are unchanged and work fine. They're the recommended way for runtime-themable values.

```scss
:root {
    --my-primary: #875A7B;
}

.element {
    color: var(--my-primary);
}
```

These don't go through Sass compilation, so they're not affected by the libsass → dart-sass migration.

---

## Model & Field Renames

## Odoo 19 — Model & Field Renames Reference

Odoo 19 contains the largest schema refactor since version 14: **130 model renames, 51 field renames, 25 module merges, 416 constraint changes**. Code referencing the old names will fail silently (table not found, KeyError on env access) or break at module install.

**Always cross-check this file when:**
- Using `self.env['some.model']` with a string model name.
- Writing a domain that references a relational field.
- Defining `_inherit = '...'` or `_inherits = {...}`.
- Writing a `<field name="...">` for a field that may have been renamed.

### Table of contents
1. Module renames
2. Module merges
3. Critical model renames (most-used)
4. Critical field renames
4b. Removed fields (`ir.cron.numbercall`, etc.)
5. The HR restructuring
6. The `res.groups` privilege refactor
7. Constraint cleanup

---

### 1. Module renames

| Old | Odoo 19 |
|---|---|
| `web_editor` | `html_builder` |
| `membership` | `partnership` |
| `pos_viva_wallet` | `pos_viva_com` |

If your `'depends'` references these, update the manifest.

### 2. Module merges (25 modules merged into parents)

| Old standalone module | Merged into |
|---|---|
| `hr_contract` | `hr` (contracts are now core HR) |
| `hr_holidays_contract` | `hr_holidays` |
| `sale_async_emails` | `sale` |
| `pos_epson_printer` | `point_of_sale` |

If you depended on `hr_contract`, change to `hr`. The `hr.contract` model itself is also renamed (see below).

### 3. Critical model renames

Odoo 19 renamed 130 models — these are the ones you'll most likely hit. **Cross-check any model name before using it.**

| Old model | Odoo 19 model | Notes |
|---|---|---|
| `hr.contract` | `hr.version` | HR contracts are now "versions". Table `hr_contract` → `hr_version`. |
| `procurement.group` | `stock.reference` | FKs across stock, purchase, sale modules. New `mrp.production.group` adds parent-child manufacturing structure. |
| `stock.quant.package` | `stock.package` | Warehouse package tracking. |
| `product.packaging` | `product.uom` | Packaging merged with UoM handling. |
| `bus.presence` | `mail.presence` | Presence moved from `bus` to `mail`. |
| `hr.candidate` | `hr.applicant` | Candidate data merged into applicant records. |
| `hr.expense.sheet` | *(removed)* | Expenses managed individually now. |
| `hr.employee.base` | *(removed)* | Inheritance chain consolidated. Custom HR modules using `_inherit = 'hr.employee.base'` need to switch to `hr.employee` directly. |
| `res.partner.title` | *(removed)* | Model gone entirely; migrate or restructure references. |
| `stock.valuation.layer` | *(removed)* | Inventory valuation now stored directly on `stock.move`. New `product.value` field logs manual updates. |

```python
## ❌ OLD — will fail in Odoo 19
contract = self.env['hr.contract'].search([])
group = self.env['procurement.group'].create({...})
package = self.env['stock.quant.package'].browse(pkg_id)

## ✅ Odoo 19
version = self.env['hr.version'].search([])
reference = self.env['stock.reference'].create({...})
package = self.env['stock.package'].browse(pkg_id)
```

For the full list of 130 renames, consult the official Odoo 19 release notes / OpenUpgrade analysis. The table above is the high-traffic subset.

### 4. Critical field renames

51 fields renamed. The ones most likely to hit your code:

| Model | Old field | Odoo 19 field |
|---|---|---|
| `res.users` | `groups_id` | `group_ids` |
| `res.groups` | `users` | `user_ids` |
| `res.groups` | `category_id` | `privilege_id` (different model — `res.groups.privilege`, not `ir.module.category`) |
| `ir.ui.menu` | `groups_id` | `group_ids` |
| `ir.ui.view` | `groups_id` | `group_ids` |
| `ir.actions.act_window` | `groups_id` | `group_ids` |
| `ir.actions.server` | `groups_id` | `group_ids` |
| `ir.actions.report` | `groups_id` | `group_ids` |
| `hr.work.entry` | `contract_id` | `version_id` (cascading from hr.contract → hr.version) |
| `sale.order.line` | `tax_id` | `tax_ids` (now supports multiple taxes per line) |
| `sale.order.line` | `product_uom` | `product_uom_id` (consistency with `_id` suffix) |
| `purchase.order.line` | `taxes_id` | `tax_ids` |
| `purchase.order.line` | `product_uom` | `product_uom_id` |
| `purchase.order` | `notes` | `note` |
| `fleet.vehicle` | `first_contract_date` | `contract_date_start` |

```python
## ❌ OLD
user.groups_id = [(6, 0, [group_admin.id])]
self.env['ir.ui.menu'].search([('groups_id', '=', g.id)])
line.tax_id = self.env['account.tax'].browse(tax_id)

## ✅ Odoo 19
from odoo import Command
user.group_ids = [Command.set([group_admin.id])]
self.env['ir.ui.menu'].search([('group_ids', '=', g.id)])
line.tax_ids = [Command.set([tax_id])]
```

In XML data files (e.g., `security.xml`):

```xml
<!-- ❌ OLD -->
<record id="my_user" model="res.users">
    <field name="groups_id" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- ✅ Odoo 19 -->
<record id="my_user" model="res.users">
    <field name="group_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

In views referencing renamed fields:

```xml
<!-- ❌ OLD sale order line view -->
<field name="product_uom"/>
<field name="tax_id" widget="many2many_tags"/>

<!-- ✅ Odoo 19 -->
<field name="product_uom_id"/>
<field name="tax_ids" widget="many2many_tags"/>
```

### 4b. Removed fields and models

Some fields and entire models were removed (no rename — they no longer exist).

#### Removed fields

| Model | Removed field | What to do |
|---|---|---|
| `ir.cron` | `numbercall` | Repeat-count concept gone. Crons run on schedule until deactivated. Remove from cron `<record>` data and any Python that read it. |
| `res.partner` | `mobile` | Use `phone` (or add a custom field if you really need to keep mobile separate). |
| `res.partner` | `last_website_so_id` | Use website-sale's request.cart logic. |
| `res.partner` | `picking_warn` | Removed alongside warning-on-partner cleanup. Migrate any logistics customizations. |
| `account.move.line` | `product_uom_category_id` | Use `product_uom_id.category_id` traversal if needed. |
| `product.uom` | `category_id` | UoM categories simplified — references now go through different relations. |
| `product.template` | `sale_line_warn` | Sale-order warnings restructured. Custom modules relying on it must adapt. |
| `account.account` | (various legacy fields) | Several deprecated fields removed; check release notes for the specific field if your code breaks. |

#### Removed models

| Old model | Status |
|---|---|
| `hr.expense.sheet` | Removed. Expenses are individual records now. |
| `hr.candidate` | Merged into `hr.applicant`. |
| `hr.employee.base` | Removed. Inheritance chain consolidated; review any `_inherit = 'hr.employee.base'`. |
| `res.partner.title` | Model removed entirely. Migrate any references. |
| `stock.valuation.layer` | Removed. Inventory valuation moved onto `stock.move` with new `product.value` field for manual updates. |

```xml
<!-- ❌ OLD — fails in Odoo 19, ir.cron has no numbercall field -->
<record id="ir_cron_my_job" model="ir.cron">
    <field name="name">My Scheduled Job</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model.run_job()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>      <!-- ← remove this line -->
    <field name="doall">1</field>
</record>

<!-- ✅ Odoo 19 -->
<record id="ir_cron_my_job" model="ir.cron">
    <field name="name">My Scheduled Job</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model.run_job()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active">True</field>
</record>
```

If you previously controlled cron lifetime via `numbercall` (e.g., set to 1 to "run once"), the new pattern is to deactivate the cron from inside its own code after the work is done:

```python
## ✅ Odoo 19 — self-deactivating cron
def run_job(self):
    self._do_work()
    self.env.ref('my_module.ir_cron_my_job').active = False
```

### 5. The HR restructuring

The HR module saw the heaviest refactor in 19:

- **`hr_contract` module merged into `hr`** — depend on `hr` only.
- **`hr.contract` → `hr.version`** — contracts are now "versions" (semver-style HR records).
- **`hr.candidate` → `hr.applicant`** — candidate model gone, fields merged into applicant.
- **`hr.expense.sheet` removed** — expenses are individual records now.
- **`hr.work.entry.contract_id` → `version_id`** — cascading rename.

If you have custom payroll/HR code, this is where Odoo 19 will hurt the most. Migrate model strings, field names, and view XPaths together.

### 6. The `res.groups` privilege refactor

Odoo 19 introduces a new model `res.groups.privilege` to organize related groups under a shared privilege concept. This is separate from `ir.module.category` (which still exists for the apps menu).

```python
## Old way to find groups in a category
self.env['res.groups'].search([('category_id', '=', cat_id)])

## Odoo 19 — privileges
self.env['res.groups'].search([('privilege_id', '=', priv_id)])
```

For most module-development tasks, the change is invisible — you reference groups by XML id (`base.group_user`, etc.) which is unchanged. The refactor matters when you query the groups model or read `category_id` on it.

### 7. Constraint cleanup

Odoo 19 removed 338 legacy SQL constraints and added 70 new ones (net 268 removed). Most are internal — but if your custom module relied on a core SQL constraint to enforce uniqueness (e.g., expecting it to fire on insert), verify the constraint still exists. The recommended approach is to declare your own constraints via the new `Constraint` class (see `orm.md`), not depend on core ones.

---

### Verification approach when in doubt

If you're unsure whether a model or field rename applies:

1. Search the project's Odoo source for the OLD name — if the source doesn't define it, it's been renamed or removed.
2. Search for the NEW name — if found, use it.
3. Check the module's `data/` migration scripts — Odoo 19's core modules include `migrations/19.0.*/` folders that contain rename scripts. The presence of a `_rename_table` or `_rename_field` call confirms the rename.

For OpenUpgrade users: the OCA OpenUpgrade project for 19.0 has the canonical list in its `migrations/` analysis files.

---
