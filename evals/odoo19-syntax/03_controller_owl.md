# Test Case 3: HTTP controller called from OWL component

## User Prompt

I'm building an Odoo 19 module. I need a controller endpoint `/library/book/search` that takes a `query` string, searches `library.book` records by name, and returns a list of `{id, name, isbn}`. The endpoint will be called from an OWL component in the backend using the rpc service.

Also write the OWL component code that calls it (just the relevant `setup()` and a `searchBooks(query)` method).

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'`.

## What we're testing

- Controller uses `type='jsonrpc'` (not `type='json'`), since web client RPC.
- Controller imports: `from odoo import http; from odoo.http import request`.
- OWL component uses the `rpc` service via `useService("rpc")`.
- OWL imports from `@odoo/owl` and `@web/core/utils/hooks`.
- `/** @odoo-module **/` directive on the JS file.

## Expected output

Two files (or two code blocks):

1. Python controller with `@http.route('/library/book/search', type='jsonrpc', auth='user')`.
2. OWL component with `setup()` getting `useService("rpc")` and `searchBooks` calling `this.rpc('/library/book/search', { query })`.

## Anti-patterns to flag

- `type='json'` for a web-client-called endpoint.
- Using `fetch` directly instead of the `rpc` service.
- jQuery `$.ajax` (legacy, gone in Odoo 17+).
