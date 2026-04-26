# ORM, Models, Fields & Methods

# Odoo 19 — Python ORM Reference

This reference covers Python model code: fields, methods, constraints, ORM operations.

## Table of contents
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

## 1. SQL constraints — use `models.Constraint`

Odoo 18 introduced the `Constraint` class as the new declarative API. In Odoo 19 it is the recommended pattern. The legacy `_sql_constraints` list still works but is being phased out.

**Use `models.Constraint(...)` directly — DO NOT import `Constraint` separately.** Just `from odoo import models` is enough.

```python
# ❌ OLD (still works, but legacy)
class Product(models.Model):
    _name = 'product.template'

    _sql_constraints = [
        ('unique_ref', 'UNIQUE(default_code)', 'Product reference must be unique.'),
        ('positive_price', 'CHECK(list_price >= 0)', 'Price must be non-negative.'),
    ]

# ✅ Odoo 19 — preferred. No separate Constraint import.
from odoo import models, fields

class Product(models.Model):
    _name = 'product.template'

    _constraints = [
        models.Constraint('unique_ref', 'UNIQUE(default_code)', 'Product reference must be unique.'),
        models.Constraint('positive_price', 'CHECK(list_price >= 0)', 'Price must be non-negative.'),
    ]
```

```python
# ❌ DON'T do this — extra import is unnecessary in Odoo 19
from odoo.models import Constraint
_constraints = [Constraint(...)]
```

`@api.constrains` decorators for Python-level constraints are unchanged — keep using them as before.

## 2. Display name — `_compute_display_name`

`name_get()` is gone. Override `_compute_display_name` instead. `display_name` is now a proper computed field, so you can `store=True` and use it in search filters / `ORDER BY`.

```python
# ❌ OLD
def name_get(self):
    result = []
    for record in self:
        name = f"{record.name} [{record.color}]" if record.color else record.name
        result.append((record.id, name))
    return result

# ✅ Odoo 19
def _compute_display_name(self):
    for record in self:
        name = f"{record.name} [{record.color}]" if record.color else record.name
        record.display_name = name
```

Inheritance pattern:

```python
# ✅ Odoo 19
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.display_name} (Custom)"
```

## 3. Command objects (replace magic tuples)

Use `Command` for One2many / Many2many writes. The tuple syntax `(0, 0, {...})` still works but is discouraged.

```python
from odoo import Command

# CREATE         old: (0, 0, vals)
Command.create({'name': 'New Line', 'qty': 1})

# UPDATE         old: (1, id, vals)
Command.update(line_id, {'qty': 2})

# DELETE (drop)  old: (2, id, 0)
Command.delete(line_id)

# UNLINK (detach without DB delete)  old: (3, id, 0)
Command.unlink(line_id)

# LINK existing  old: (4, id, 0)
Command.link(line_id)

# CLEAR all      old: (5, 0, 0)
Command.clear()

# SET full list  old: (6, 0, [ids])
Command.set([id1, id2, id3])
```

Real-world example:

```python
# ✅ Odoo 19
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
# ❌ WRONG — ImportError
from odoo.fields import Command

# ✅ CORRECT
from odoo import Command
```

## 4. `_read_group()` API

`read_group()` (returning list of dicts with `[id, display_name]` tuples for relational fields) is replaced by `_read_group()` returning tuples with actual recordsets.

```python
# ❌ OLD
results = self.env['account.move.line'].read_group(
    domain=[('move_id.state', '=', 'posted')],
    fields=['account_id', 'debit:sum', 'credit:sum'],
    groupby=['account_id'],
)
for group in results:
    account_name = group['account_id'][1]   # tuple unpacking
    print(account_name, group['debit'], group['credit'])

# ✅ Odoo 19
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

## 5. `Markup()` for HTML in Python (Odoo 17+ still required in 19)

Raw HTML string concatenation is unsafe. All HTML written from Python must use `markupsafe.Markup`. This applies to `message_post`, computed HTML fields, controller responses, etc.

```python
# ❌ OLD — XSS risk
def _get_description(self):
    return "<p>Hello <b>" + self.name + "</b></p>"

# ✅ Odoo 19
from markupsafe import Markup, escape

def _get_description(self):
    return Markup("<p>Hello <b>%s</b></p>") % escape(self.name)
```

`message_post`:

```python
# ✅ Odoo 19
from markupsafe import Markup, escape

self.message_post(
    body=Markup("<p>Invoice <b>%s</b> confirmed</p>") % escape(invoice.name)
)
```

**Pitfall — f-strings inside `Markup()` do NOT escape:**

```python
# ❌ XSS — Markup marks the whole thing safe, including the user input
body = Markup(f"<p>Hello {user_input}</p>")

# ✅ Use % formatting with explicit escape() or rely on % auto-escaping str args
body = Markup("<p>Hello %s</p>") % escape(user_input)
```

## 6. Cache invalidation and flush (granular)

The blanket `flush()` and `invalidate_cache()` are gone. Use the recordset/model-level versions.

```python
# ❌ OLD
self.env['res.partner'].invalidate_cache(['name', 'email'])
self.env['res.partner'].flush()

# ✅ Odoo 19 — recordset level
records.invalidate_recordset(['name', 'email'])
records.flush_recordset(['name', 'email'])

# ✅ Odoo 19 — model level
self.env['res.partner'].invalidate_model(['name'])
self.env['res.partner'].flush_model(['name'])
```

`_flush_search()` is deprecated. Flushing is handled by `execute_query()` based on metadata in the SQL object.

## 7. Access rights — combined methods

Odoo 19 introduces methods that combine access rights AND record rules in a single call:

```python
# ✅ Odoo 19
record.check_access('write')        # raises AccessError if denied
record.has_access('write')           # returns bool
allowed = records._filtered_access('read')   # returns subset accessible to current user
```

Use these instead of the older split `check_access_rights` / `check_access_rule` pattern when you want both checks together.

## 8. Search by display name

`_name_search` is no longer the place to override search-by-name behavior. Implement `_search_display_name` instead, like any other field's search method.

```python
# ✅ Odoo 19
@api.model
def _search_display_name(self, operator, value):
    # custom search logic, returns a domain
    return [('name', operator, value), ('code', operator, value)]
```

## 9. `aggregator` instead of `group_operator`

The `group_operator` parameter on Field is renamed to `aggregator`.

```python
# ❌ OLD
amount = fields.Float(group_operator='avg')

# ✅ Odoo 19
amount = fields.Float(aggregator='avg')
```

## 10. Removed / deprecated items

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

## 11. Imports and small gotchas

- `from odoo import Command` — not `odoo.fields`.
- For `Constraint`, just use `models.Constraint(...)` after `from odoo import models`. No separate import needed.
- `from markupsafe import Markup, escape` for HTML.
- `from odoo.osv.expression import OR` is **deprecated** in Odoo 19. Use `Domain.OR` (see section 16).
- `odoo.osv` module is deprecated overall — prefer `odoo.Domain` API and `odoo.fields` for field types.
- Many model names changed in Odoo 19 — always check `model_renames.md` before referencing a model by string.

## 12. Deprecated `record._cr`, `record._context`, `record._uid`

The shortcut attributes on records are deprecated in Odoo 19. Use `record.env.*` instead.

```python
# ❌ OLD / deprecated in Odoo 19
self._cr.execute("SELECT ...")
ctx = self._context
uid = self._uid

# ✅ Odoo 19
self.env.cr.execute("SELECT ...")
ctx = self.env.context
uid = self.env.uid
```

This applies in any model method, controller, or wizard. The deprecation also extends to `self._context` patterns commonly used to read context flags.

## 13. `read_group()` deprecated → `_read_group()` or `formatted_read_group()`

The public `read_group()` method is deprecated in Odoo 19. Two replacements depending on the use case:

- **`_read_group()`** — for **backend / Python** usage (returns tuples with real recordsets, see section 4).
- **`formatted_read_group()`** — formatted public API, for cases where you previously needed `read_group`'s dict format.

```python
# ❌ OLD — deprecated in 19
results = self.env['account.move.line'].read_group(
    domain=[('state', '=', 'posted')],
    fields=['account_id', 'debit:sum'],
    groupby=['account_id'],
)

# ✅ Odoo 19 — backend usage (preferred)
results = self.env['account.move.line']._read_group(
    domain=[('state', '=', 'posted')],
    groupby=['account_id'],
    aggregates=['debit:sum'],
)
for account, debit_sum in results:
    ...

# ✅ Odoo 19 — public/formatted API
results = self.env['account.move.line'].formatted_read_group(
    domain=[('state', '=', 'posted')],
    groupby=['account_id'],
    aggregates=['debit:sum'],
)
```

## 14. New `@api.private` decorator

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

## 15. `@api.returns` decorator REMOVED

`@api.returns(...)` is removed in Odoo 19. Use modern API patterns — return recordsets directly, or use type hints if needed for clarity.

```python
# ❌ OLD — ImportError or no-op in Odoo 19
@api.returns('res.partner', lambda value: value.id)
def my_method(self):
    return self.env['res.partner'].browse(...)

# ✅ Odoo 19 — just return the recordset
def my_method(self):
    return self.env['res.partner'].browse(...)
```

## 16. New domain API — `Domain` class and `any`/`not any` operators

Odoo 19 introduces a proper `Domain` class (`odoo.Domain`) replacing the older `osv.expression` helpers, plus new domain operators for relational traversal.

### `Domain.OR` / `Domain.AND` replace `expression.OR` / `expression.AND`

```python
# ❌ OLD / deprecated in Odoo 19
from odoo.osv.expression import OR, AND
combined = OR([domain_a, domain_b])

# ✅ Odoo 19
from odoo import Domain
combined = Domain.OR([domain_a, domain_b])
# or:
combined = Domain.AND([domain_a, domain_b])
```

### `any` / `not any` operators for relational fields

For querying related models in a domain (instead of dot-notation traversal), Odoo 19 supports `any` and `not any`:

```python
# ✅ Odoo 19
# "find partners that have any sale order in state 'sale'"
domain = [('sale_order_ids', 'any', [('state', '=', 'sale')])]

# "find partners with NO sale order in 'cancel' state"
domain = [('sale_order_ids', 'not any', [('state', '=', 'cancel')])]
```

There are also **internal-only** operators `any!` and `not any!` that bypass access rights and record rules. **NEVER use `any!`/`not any!` in domains coming from RPC/user input** — they're for trusted server-side logic only (computed fields, cron jobs, internal queries).

```python
# ✅ Odoo 19 — server-side only, bypasses access rights
domain = [('document_ids', 'any!', [('confidential', '=', True)])]
```

### Domain operators must be lowercase

Since 19.0, uppercase operators raise a deprecation warning. Always lowercase:

```python
# ❌ Triggers DeprecationWarning in 19
[('name', 'LIKE', 'foo')]
[('state', 'IN', ['draft', 'sent'])]

# ✅ Odoo 19
[('name', 'like', 'foo')]
[('state', 'in', ['draft', 'sent'])]
```

### Custom SQL in domains via `Domain.custom`

For injecting custom SQL into a domain (replacing legacy patterns that subclassed expression):

```python
# ✅ Odoo 19
from odoo import Domain
from odoo.tools import SQL

domain = Domain.custom(to_sql=lambda model, alias, query: SQL("...custom condition..."))
```

## 17. `check_access_rights` → `check_access`

The split methods are merged. Use `check_access` (raises) or `has_access` (bool) — see section 7 for details.

```python
# ❌ OLD
record.check_access_rights('write')
record.check_access_rule('write')

# ✅ Odoo 19 — combined
record.check_access('write')          # raises
record.has_access('write')            # bool
```

## 18. `env.tz`, `env.company`, `env.companies` — modern context APIs

Odoo 19 standardizes a few env-level helpers:

- **`env.tz`** — current timezone (string), replaces old `self._context.get('tz')` patterns.
- **`env.company`** — the active company recordset (single).
- **`env.companies`** — companies the user is currently allowed to operate in (recordset).

```python
# ❌ OLD
tz = self._context.get('tz') or self.env.user.tz
allowed_companies = self.env.context.get('allowed_company_ids', [])

# ✅ Odoo 19
tz = self.env.tz
active_company = self.env.company
allowed_companies = self.env.companies
```

For multi-company filtering, prefer `env.companies` over manual context inspection.
