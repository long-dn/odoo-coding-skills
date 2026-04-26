# HTTP Controllers

# Odoo 19 — Controllers Reference

This reference covers HTTP controllers, route types, and authentication.

## Table of contents
1. `type="json"` → `type="jsonrpc"` for web-client RPC
2. `auth="bearer"` for API tokens
3. Three route types — when to use each
4. Common pitfalls

---

## 1. `type="json"` vs `type="jsonrpc"`

Odoo 17 split JSON endpoints into two types and renamed the JSON-RPC variant. Odoo 19 keeps this distinction. The Odoo web client (calls from JS via `rpc` service) uses **JSON-RPC 2.0** — endpoints called by the web client must declare `type="jsonrpc"`.

```python
# ❌ OLD — works for plain JSON only, web client RPC will fail
@http.route('/my_module/get_data', type='json', auth='user')
def get_data(self, **kwargs):
    return {'data': request.env['my.model'].search([]).read(['name'])}

# ✅ Odoo 19 — for endpoints called by the Odoo web client (JS rpc service)
@http.route('/my_module/get_data', type='jsonrpc', auth='user')
def get_data(self, **kwargs):
    return {'data': request.env['my.model'].search([]).read(['name'])}
```

The Python signature and return shape are identical — only the `type` parameter changes. The same names are still imported the same way:

```python
from odoo import http
from odoo.http import request
```

## 2. `auth="bearer"` for API tokens

For external API consumers using bearer tokens (e.g., third-party integrations), use `auth="bearer"`:

```python
# ✅ Odoo 19
@http.route('/api/v1/resource', auth='bearer', type='jsonrpc')
def api_resource(self):
    return {'user': request.env.user.name}
```

The token is sent as `Authorization: Bearer <token>` header. Configure tokens via `res.users.apikeys` (UI: Developer Mode → user form → API Keys).

## 3. The three route types — when to use each

| `type` | When to use |
|---|---|
| `http` | Plain HTTP endpoints returning HTML, files, redirects. Public pages, file downloads. |
| `jsonrpc` | Endpoints called by the Odoo web client via the `rpc` service. JSON-RPC 2.0 protocol. |
| `json` | Plain JSON request/response (POST with JSON body, get JSON back) — for non-Odoo callers that don't speak JSON-RPC. |

Examples:

```python
# Public web page
@http.route('/about', type='http', auth='public', website=True)
def about(self):
    return request.render('my_module.about_page')

# Web-client RPC (called from OWL with rpc('/my_module/data', {...}))
@http.route('/my_module/data', type='jsonrpc', auth='user')
def data(self, **kw):
    return {'records': [...]}

# REST-ish JSON for an external integration
@http.route('/api/v1/orders', type='json', auth='bearer', methods=['POST'], csrf=False)
def create_order(self, **payload):
    order = request.env['sale.order'].create(payload)
    return {'id': order.id}
```

## 4. Common pitfalls

### The Phantom JSON Endpoint
Forgetting `type="json"` → `type="jsonrpc"` for endpoints called by the Odoo web client. Symptom: silent failure, cryptic 404s, JSON parsing errors in browser console. Always check whether the caller is the web client (use `jsonrpc`) or an external system (use `json`).

### CSRF on POST endpoints
Public POST endpoints called by external systems need `csrf=False`. Endpoints called by the web client get the CSRF token automatically.

### Auth modes
- `auth='public'` — anyone, no login. Use sparingly.
- `auth='user'` — must be logged in.
- `auth='bearer'` — API token (Odoo 17+).
- `auth='none'` — no env, raw request. Almost never what you want.

### `request` import
Import is unchanged: `from odoo.http import request`. Inside controllers, `request.env` gives you the environment, `request.httprequest` is the WSGI/Werkzeug request.
