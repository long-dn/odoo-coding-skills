# Test Case 9: Deprecated `_context`/`_cr`/`_uid` patterns

## User Prompt

I'm migrating this Odoo 17 method to Odoo 19. Please update the syntax:

```python
def my_action(self):
    if self._context.get('skip_validation'):
        return
    company_ids = self._context.get('allowed_company_ids', [])
    user_tz = self._context.get('tz') or self.env.user.tz

    self._cr.execute("SELECT id FROM res_partner WHERE active = TRUE")
    partner_ids = [r[0] for r in self._cr.fetchall()]

    return {
        'name': 'Partners',
        'context': {'default_user_id': self._uid},
    }
```

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'`.

## What we're testing

- Replace `self._context` with `self.env.context`
- Replace `self._cr` with `self.env.cr`
- Replace `self._uid` with `self.env.uid`
- Replace `self._context.get('tz')` with `self.env.tz`
- Replace `self._context.get('allowed_company_ids')` with `self.env.companies`

## Expected output

A migrated method using `self.env.*` consistently:

```python
def my_action(self):
    if self.env.context.get('skip_validation'):
        return
    allowed_companies = self.env.companies
    user_tz = self.env.tz

    self.env.cr.execute("SELECT id FROM res_partner WHERE active = TRUE")
    partner_ids = [r[0] for r in self.env.cr.fetchall()]

    return {
        'name': 'Partners',
        'context': {'default_user_id': self.env.uid},
    }
```

## Anti-patterns to flag

- Any remaining `self._context`, `self._cr`, `self._uid` references.
- Reading `tz` or `allowed_company_ids` from context manually when `env.tz` / `env.companies` exist.
