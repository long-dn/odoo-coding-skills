# Test Case 4: Model rename trap — hr.contract

## User Prompt

In my Odoo 19 module, I want to add a method to res.partner that counts how many active HR contracts the partner has (as `employee_id.partner_id`). Write the computed field and method.

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'` and `'depends': ['hr']`.

## What we're testing

- Does Claude know `hr.contract` was renamed to `hr.version` in Odoo 19?
- Does the method use `self.env['hr.version']` and not `self.env['hr.contract']`?
- This is the silent-failure category — `self.env['hr.contract']` will raise `KeyError` at runtime.

## Expected output

A computed field on `res.partner` (e.g., `active_contract_count`) and a `_compute_active_contract_count` method that does:

```python
contracts = self.env['hr.version'].search([
    ('employee_id.partner_id', '=', self.id),
    ('state', '=', 'open'),  # or whatever the active state is
])
```

Or some variation, but the model name MUST be `hr.version`, not `hr.contract`.

## Anti-patterns to flag

- `self.env['hr.contract']` anywhere.
- `_inherit = 'hr.contract'`.
- `Many2one('hr.contract', ...)`.
