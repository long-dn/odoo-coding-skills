---
applyTo: "**/*.py,**/*.xml"
---

# Odoo 19 — Model & Field Renames Reference

Odoo 19 contains the largest schema refactor since version 14: **130 model renames, 51 field renames, 25 module merges, 416 constraint changes**. Code referencing the old names will fail silently (table not found, KeyError on env access) or break at module install.

**Always cross-check this file when:**
- Using `self.env['some.model']` with a string model name.
- Writing a domain that references a relational field.
- Defining `_inherit = '...'` or `_inherits = {...}`.
- Writing a `<field name="...">` for a field that may have been renamed.

## Table of contents
1. Module renames
2. Module merges
3. Critical model renames (most-used)
4. Critical field renames
4b. Removed fields (`ir.cron.numbercall`, etc.)
5. The HR restructuring
6. The `res.groups` privilege refactor
7. Constraint cleanup

---

## 1. Module renames

| Old | Odoo 19 |
|---|---|
| `web_editor` | `html_builder` |
| `membership` | `partnership` |
| `pos_viva_wallet` | `pos_viva_com` |

If your `'depends'` references these, update the manifest.

## 2. Module merges (25 modules merged into parents)

| Old standalone module | Merged into |
|---|---|
| `hr_contract` | `hr` (contracts are now core HR) |
| `hr_holidays_contract` | `hr_holidays` |
| `sale_async_emails` | `sale` |
| `pos_epson_printer` | `point_of_sale` |

If you depended on `hr_contract`, change to `hr`. The `hr.contract` model itself is also renamed (see below).

## 3. Critical model renames

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
# ❌ OLD — will fail in Odoo 19
contract = self.env['hr.contract'].search([])
group = self.env['procurement.group'].create({...})
package = self.env['stock.quant.package'].browse(pkg_id)

# ✅ Odoo 19
version = self.env['hr.version'].search([])
reference = self.env['stock.reference'].create({...})
package = self.env['stock.package'].browse(pkg_id)
```

For the full list of 130 renames, consult the official Odoo 19 release notes / OpenUpgrade analysis. The table above is the high-traffic subset.

## 4. Critical field renames

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
# ❌ OLD
user.groups_id = [(6, 0, [group_admin.id])]
self.env['ir.ui.menu'].search([('groups_id', '=', g.id)])
line.tax_id = self.env['account.tax'].browse(tax_id)

# ✅ Odoo 19
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

## 4b. Removed fields and models

Some fields and entire models were removed (no rename — they no longer exist).

### Removed fields

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

### Removed models

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
# ✅ Odoo 19 — self-deactivating cron
def run_job(self):
    self._do_work()
    self.env.ref('my_module.ir_cron_my_job').active = False
```

## 5. The HR restructuring

The HR module saw the heaviest refactor in 19:

- **`hr_contract` module merged into `hr`** — depend on `hr` only.
- **`hr.contract` → `hr.version`** — contracts are now "versions" (semver-style HR records).
- **`hr.candidate` → `hr.applicant`** — candidate model gone, fields merged into applicant.
- **`hr.expense.sheet` removed** — expenses are individual records now.
- **`hr.work.entry.contract_id` → `version_id`** — cascading rename.

If you have custom payroll/HR code, this is where Odoo 19 will hurt the most. Migrate model strings, field names, and view XPaths together.

## 6. The `res.groups` privilege refactor

Odoo 19 introduces a new model `res.groups.privilege` to organize related groups under a shared privilege concept. This is separate from `ir.module.category` (which still exists for the apps menu).

```python
# Old way to find groups in a category
self.env['res.groups'].search([('category_id', '=', cat_id)])

# Odoo 19 — privileges
self.env['res.groups'].search([('privilege_id', '=', priv_id)])
```

For most module-development tasks, the change is invisible — you reference groups by XML id (`base.group_user`, etc.) which is unchanged. The refactor matters when you query the groups model or read `category_id` on it.

## 7. Constraint cleanup

Odoo 19 removed 338 legacy SQL constraints and added 70 new ones (net 268 removed). Most are internal — but if your custom module relied on a core SQL constraint to enforce uniqueness (e.g., expecting it to fire on insert), verify the constraint still exists. The recommended approach is to declare your own constraints via the new `Constraint` class (see `orm.md`), not depend on core ones.

---

## Verification approach when in doubt

If you're unsure whether a model or field rename applies:

1. Search the project's Odoo source for the OLD name — if the source doesn't define it, it's been renamed or removed.
2. Search for the NEW name — if found, use it.
3. Check the module's `data/` migration scripts — Odoo 19's core modules include `migrations/19.0.*/` folders that contain rename scripts. The presence of a `_rename_table` or `_rename_field` call confirms the rename.

For OpenUpgrade users: the OCA OpenUpgrade project for 19.0 has the canonical list in its `migrations/` analysis files.
