# Test Case 1: Create model with SQL constraint in Odoo 19

## User Prompt

I'm working on an Odoo 19 module. Please write me a model `library.book` with these fields:
- `name` (Char, required)
- `isbn` (Char, must be unique)
- `pages` (Integer, must be >= 0)
- `author_id` (Many2one to res.partner)

Add appropriate SQL constraints for uniqueness and the page count check.

## Project context (manifest)

```python
# __manifest__.py
{
    'name': 'Library',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
}
```

## What we're testing

- Does Claude detect Odoo 19 from the manifest?
- Does Claude use `_constraints = [Constraint(...)]` instead of `_sql_constraints`?
- Does Claude import `Constraint` correctly (`from odoo.models import Constraint`)?

## Expected output (key elements)

- A model class with the four fields.
- `_constraints` list using `models.Constraint(...)` (with `models.` prefix, not bare `Constraint(...)`).
- Just `from odoo import models, fields` — NO separate `from odoo.models import Constraint` line.
- No `_sql_constraints` anywhere in the code.
