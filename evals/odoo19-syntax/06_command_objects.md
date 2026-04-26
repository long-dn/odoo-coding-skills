# Test Case 6: O2M / M2M writes — Command objects

## User Prompt

In an Odoo 19 module, write a method `create_order_with_lines(self, partner, products)` on `sale.order` that:
- Creates a sale order for the given partner.
- Creates one order line for each product in `products` (each is a tuple `(product, qty)`).
- Tags the order with two tags (assume `tag_a` and `tag_b` are records in scope) — REPLACING any existing tags.

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'` and `'depends': ['sale']`.

## What we're testing

- Does Claude use `Command.create({...})` instead of `(0, 0, {...})`?
- Does Claude use `Command.set([id1, id2])` instead of `(6, 0, [id1, id2])`?
- Correct import: `from odoo import Command` (NOT `from odoo.fields import Command`).

## Expected output

Method body something like:

```python
from odoo import Command, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_order_with_lines(self, partner, products):
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                Command.create({'product_id': p.id, 'product_uom_qty': qty})
                for p, qty in products
            ],
            'tag_ids': [Command.set([tag_a.id, tag_b.id])],
        })
```

## Anti-patterns to flag

- `(0, 0, {...})`, `(6, 0, [...])` tuple syntax.
- `from odoo.fields import Command` (wrong path).
