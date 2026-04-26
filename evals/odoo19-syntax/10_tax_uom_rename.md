# Test Case 10: Sale order line — renamed `tax_id` and `product_uom` fields

## User Prompt

In my Odoo 19 module, write a method that creates a sale order with one line for product `prod`, qty 5, on UoM `uom_unit`, with two taxes `tax_5pct` and `tax_10pct`. The order is for partner `partner`.

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'` and `'depends': ['sale']`.

## What we're testing

- Does Claude know `sale.order.line.tax_id` was renamed to `tax_ids` (plural, supports multiple taxes)?
- Does Claude know `sale.order.line.product_uom` was renamed to `product_uom_id`?
- Bonus: uses `Command.set([...])` for the M2M tax_ids relation.

## Expected output

```python
from odoo import Command

self.env['sale.order'].create({
    'partner_id': partner.id,
    'order_line': [
        Command.create({
            'product_id': prod.id,
            'product_uom_qty': 5,
            'product_uom_id': uom_unit.id,        # ← _id suffix
            'tax_ids': [Command.set([tax_5pct.id, tax_10pct.id])],  # ← plural
        }),
    ],
})
```

## Anti-patterns to flag

- `'product_uom': uom_unit.id` (old field name without `_id`).
- `'tax_id': tax_5pct.id` (old singular field).
- `'taxes_id': [...]` (this was the purchase.order.line old name).
