# Manifest, Hooks & Security

# Odoo 19 — Manifest, Hooks & Security Reference

This reference covers `__manifest__.py`, install/upgrade hooks, asset bundles, and security file conventions.

## Table of contents
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

## 1. `__manifest__.py` shape

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

## 2. `license` is mandatory

Since Odoo 17, omitting `'license'` raises an error on install. Common values:
- `'LGPL-3'` (most permissive for proprietary use)
- `'AGPL-3'`
- `'OPL-1'` (Odoo Proprietary License — for paid modules)
- `'Other proprietary'`

## 3. `version` field

Must start with `19.0` for an Odoo 19 module. Convention: `'19.0.MAJOR.MINOR.PATCH'` — e.g., `'19.0.1.0.0'`.

If you skip the `19.0.` prefix and write just `'1.0.0'`, Odoo prepends its own version, which can cause unexpected upgrade-script execution.

## 4. Asset bundles

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

## 5. Hook signatures

Install/upgrade/uninstall hooks now receive `env` directly (Odoo 17+). The old `(cr, registry)` signature is gone.

```python
# ❌ OLD
def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['my.model'].search([])._do_something()

# ✅ Odoo 19
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

## 6. Security — `ir.model.access.csv`

Standard CSV format (unchanged in 19):

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
```

Record rules in `ir.rule` use `domain_force` — domains in record rules are unchanged syntactically, but if your domain references the renamed user-group field on `res.users`, see section 8.

## 7. The `res.groups` privilege refactor (NEW in Odoo 19)

Odoo 19 introduces `res.groups.privilege` — a model that groups related security groups for cleaner privilege management.

```python
# Old: groups had categories via res.groups.category_id (a M2O to ir.module.category)
# Odoo 19: res.groups now has privilege_id (M2O to res.groups.privilege)
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

## 8. `groups_id` → `group_ids` rename

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
# ❌ OLD code that breaks in 19
user.groups_id |= self.env.ref('sale.group_sale_manager')

# ✅ Odoo 19
user.group_ids |= self.env.ref('sale.group_sale_manager')

# In domains:
# ❌  ('groups_id', 'in', [...])
# ✅  ('group_ids', 'in', [...])
```

Record rules with `domain_force` referencing these fields need to be updated too.

## 9. Python version and dependencies

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

## 10. Server config — `xmlrpc_port` → `http_port`

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

## 11. Demo data not loaded by default

Odoo 19 changed the default: demo data is **no longer loaded automatically** when creating a new database. Pass `--without-demo=False` (or set explicitly in config) if you actually want demo data. For tests, this means tests that previously relied on demo records present "by accident" must declare those records explicitly via test data files or `setUp`.
