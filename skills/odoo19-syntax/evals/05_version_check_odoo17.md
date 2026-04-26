# Test Case 5: VERSION CHECK — project is Odoo 17, not Odoo 19

## User Prompt

I have an Odoo project. Please add a `_sql_constraints` for unique email on the `res.partner` model (in a custom module that inherits it).

## Project context (manifest)

```python
# __manifest__.py
{
    'name': 'Partner Email Unique',
    'version': '17.0.1.0.0',     # ← Odoo 17, NOT 19
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
}
```

## What we're testing — THE MOST IMPORTANT TEST

- Does Claude check the version BEFORE applying syntax rules?
- Does Claude detect that this is Odoo 17 (from the version field)?
- Does Claude SKIP the Odoo 19 conventions and write Odoo 17 syntax?
- This means: the response should USE `_sql_constraints` (which is correct for Odoo 17) and NOT use the new `Constraint` class.
- Bonus: Claude should mention that it detected Odoo 17 and is using Odoo 17 syntax (not Odoo 19).

## Expected output

Code using `_sql_constraints = [('unique_email', 'UNIQUE(email)', '...')]` — the legacy syntax that's correct for Odoo 17.

## Anti-pattern to flag

- Using `_constraints = [Constraint(...)]` here would be WRONG, even though the user said "Odoo project". Odoo 17 doesn't have `models.Constraint`.
- Silently applying Odoo 19 syntax without acknowledging the version mismatch.
