# Test Case 11: Domain construction with `any` operator and `Domain.OR`

## User Prompt

In an Odoo 19 module, write a search method on `res.partner` that returns partners matching either of these conditions:
- The partner has at least one sale order in state 'sale'
- OR the partner's name starts with "VIP"

Combine the two with OR logic. Use the modern Odoo 19 domain API.

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'` and `'depends': ['sale']`.

## What we're testing

- Use of new `any` operator for relational subquery (`('sale_order_ids', 'any', [('state', '=', 'sale')])`)
- Use of `Domain.OR` (not `from odoo.osv.expression import OR`)
- Lowercase domain operators
- Import: `from odoo import Domain` (not `osv.expression`)

## Expected output

```python
from odoo import Domain, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def find_vip_or_active(self):
        domain_a = [('sale_order_ids', 'any', [('state', '=', 'sale')])]
        domain_b = [('name', '=like', 'VIP%')]
        combined = Domain.OR([domain_a, domain_b])
        return self.search(combined)
```

(The exact method body can vary; the import and operator usage are what matters.)

## Anti-patterns to flag

- `from odoo.osv.expression import OR` (deprecated path).
- Using uppercase operators like `'LIKE'` or `'IN'`.
- Using dot-notation like `('sale_order_ids.state', '=', 'sale')` — works but `any` is preferred.
- Building domain with `'|'` prefix inline when the question explicitly asks for the modern API.
