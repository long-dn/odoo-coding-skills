# Odoo 19 — OWL & JavaScript Reference

This reference covers OWL 2 components, services, and the modern JS architecture used in `static/src/`. Odoo 17 finalized the move to OWL 2 and the new JS service layer; Odoo 19 continues those conventions.

## Table of contents
1. OWL 2 component basics
2. Frozen `env` — use `useSubEnv`
3. No more `t-ref` to child components
4. No `class`/`style` auto-forwarding to root element
5. `t-on` callbacks → prefer prop callbacks
6. Patching components (`patch` from `@web/core/utils/patch`)
7. RPC calls — import plain `rpc`
8. Services and `useService`
9. Registry and component registration
10. Removed jQuery & legacy widgets
11. CSP — no inline scripts, no CDN injection
12. POS — `get_order()` → `getOrder()` (camelCase rename)
13. New `useSortable` hook
14. Website / eCommerce — `request.cart` and `request.pricelist`

---

## 1. OWL 2 component basics

An Odoo 19 OWL component is a class with a `static template` reference and lifecycle hooks via the `setup()` method.

```javascript
/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyWidget extends Component {
    static template = "my_module.MyWidget";
    static props = {
        record: { type: Object, optional: true },
    };

    setup() {
        this.state = useState({ count: 0 });
        onMounted(() => console.log("mounted"));
    }

    increment() {
        this.state.count++;
    }
}

registry.category("fields").add("my_widget", { component: MyWidget });
```

Key points for OWL 2:
- Components extend `Component` from `@odoo/owl`.
- `setup()` replaces constructor logic and is where hooks (`useState`, `useService`, `useRef`, etc.) are called.
- `static template` is a string reference to a QWeb template name.
- `static props` declares accepted props (validated at runtime in dev).

## 2. Frozen `env` — use `useSubEnv` to extend it

In OWL 2, `env` is frozen and cannot be mutated. To pass data to descendant components, use `useSubEnv` (from `@odoo/owl`):

```javascript
// ❌ OLD (OWL 1)
this.env.myValue = 42;

// ✅ Odoo 19 (OWL 2)
import { Component, useSubEnv } from "@odoo/owl";

export class Parent extends Component {
    setup() {
        useSubEnv({ myValue: 42 });
    }
}
```

Children read it as `this.env.myValue`.

## 3. No more `t-ref` to child components

In OWL 1, `t-ref` could grab a reference to a child component instance. In OWL 2 it only refs DOM elements.

```xml
<!-- ❌ OLD — gets child component instance in OWL 1, doesn't work in 2 -->
<MyChild t-ref="child"/>

<!-- ✅ Odoo 19 — t-ref only refs HTML elements -->
<div t-ref="myDiv"/>
```

```javascript
import { Component, useRef } from "@odoo/owl";

export class Parent extends Component {
    setup() {
        this.myDiv = useRef("myDiv");   // refs the <div>, not a component
    }
}
```

To communicate with children, pass props (including callbacks) and let children call back up.

## 4. No `class`/`style` auto-forwarding to root element

In OWL 1, putting `class="..."` on a `<MyChild>` tag would forward to the child's root DOM. In OWL 2 these are now plain props — the child must explicitly use them in its template.

```xml
<!-- Parent -->
<MyChild class="'extra-class'" style="'color: red'"/>
<!-- Note: must be JS expression, hence the string quotes -->

<!-- Child template — must explicitly apply -->
<div t-att-class="props.class" t-att-style="props.style">
    ...
</div>
```

## 5. `t-on` callbacks — prefer prop callbacks

For parent ↔ child communication, OWL 2 favors callback props over `t-on` event listeners.

```javascript
// Parent passes a callback
export class Parent extends Component {
    static template = "Parent";
    onChildClick(value) {
        console.log("child said", value);
    }
}
```

```xml
<!-- Parent template -->
<MyChild onClick.bind="onChildClick"/>
```

```javascript
// Child invokes the callback
export class MyChild extends Component {
    static template = "MyChild";
    static props = { onClick: Function };
    handle() {
        this.props.onClick("hello");
    }
}
```

`t-on:click` is still valid for binding to native DOM events on actual HTML elements inside a template.

## 6. Patching components

To patch an existing OWL component (instead of overriding via class extension), use the `patch` utility:

```javascript
/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup();
        // additional setup
    },

    async saveRecord(...args) {
        console.log("saving");
        return super.saveRecord(...args);
    },
});
```

Notes:
- Use `super.method(...)` to call the original.
- `patch` mutates the prototype; use it sparingly for core components.
- The third argument (legacy `{...}` options object) is removed in modern Odoo — just pass two args: target and patch object.

## 7. RPC calls — plain `rpc` function

Don't use raw `fetch` for Odoo backend calls. In Odoo 19, `rpc` is exported as a plain function from `@web/core/network/rpc`; it is not a service and must not be requested with `useService("rpc")`.

```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class MyComponent extends Component {
    async loadData() {
        const result = await rpc("/my_module/get_data", {
            ids: [1, 2, 3],
        });
        return result;
    }
}
```

The matching Python controller should use `type='jsonrpc'` (see `controllers.md`).

For ORM calls, use the `orm` service:

```javascript
this.orm = useService("orm");
const records = await this.orm.searchRead("res.partner", [["is_company", "=", true]], ["name", "email"]);
```

## 8. Services and `useService`

Common services (request via `useService("name")`):
- `"orm"` — ORM operations (search, read, create, write, unlink, call).
- `"notification"` — show toast notifications.
- `"dialog"` — open a dialog.
- `"action"` — execute Odoo actions (open form, run server action).
- `"user"` — current user info, has_group, etc.
- `"router"` — URL/state.

```javascript
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MyView extends Component {
    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
    }
    notify() {
        this.notification.add("Saved!", { type: "success" });
    }
    openPartners() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            views: [[false, "list"], [false, "form"]],
        });
    }
}
```

## 9. Registry and component registration

Register custom widgets, fields, services via the central `registry`:

```javascript
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

// Register a field widget
registry.category("fields").add("my_widget", { component: MyWidget });

// Register a service
registry.category("services").add("myService", {
    start() {
        return { doThing: () => rpc("/my/route", {}) };
    },
});

// Register a view (uncommon)
registry.category("views").add("my_view", { ... });
```

Common categories: `fields`, `services`, `views`, `actions`, `main_components`, `systray`.

## 10. No more jQuery or legacy widgets

- No `$.fn.myPlugin(...)` — jQuery is no longer included by default (Odoo 17+).
- The `web.Widget` legacy class is gone in Odoo 19. All UI is OWL.
- The `core.bus` event bus pattern is replaced by services and reactive state.

## 11. CSP — no inline scripts, no CDN injection

Odoo 18+ enforces strict Content Security Policy. Two patterns that BREAK:

```javascript
// ❌ BREAKS — CSP blocks inline script creation with external src
const s = document.createElement("script");
s.src = "https://cdn.example.com/lib.js";
document.head.appendChild(s);
```

```xml
<!-- ❌ BREAKS — no inline <script> in QWeb -->
<t t-name="MyTemplate">
    <script>console.log("hi");</script>
</t>
```

Vendor third-party libraries into your module's `static/lib/` and declare them in the asset bundle:

```python
# __manifest__.py
{
    'assets': {
        'web.assets_backend': [
            'my_module/static/lib/some-library/some-library.min.js',
            'my_module/static/src/js/my_component.js',
            'my_module/static/src/xml/my_template.xml',
        ],
    },
}
```

QWeb templates are loaded from XML files declared in the same asset bundle.

## 12. POS — `get_order()` → `getOrder()` (camelCase rename)

Point of Sale's JS API moved its order-access method to camelCase to match the rest of the JS codebase:

```javascript
// ❌ OLD
const order = this.pos.get_order();

// ✅ Odoo 19
const order = this.pos.getOrder();
```

This is part of a broader naming consistency effort in the POS module. If you patch or extend POS components, audit all `pos.snake_case_method()` calls — many have been or will be renamed to `camelCase`. The Odoo POS frontend is the most affected area.

## 13. New `useSortable` hook

Odoo 19 ships a `useSortable` hook for drag-and-drop ordering of records, useful for kanban-style or list reordering:

```javascript
import { Component, useRef } from "@odoo/owl";
import { useSortable } from "@web/core/utils/sortable_owl";

export class MyList extends Component {
    setup() {
        this.listRef = useRef("list");
        useSortable({
            ref: this.listRef,
            elements: ".sortable-item",
            onDrop: ({ element, previous, next }) => {
                // reorder logic
            },
        });
    }
}
```

## 14. Website / eCommerce — `request.cart` and `request.pricelist`

For modules that touched the website-sale flow:

```python
# ❌ OLD
order = request.website.sale_get_order()
pricelist = request.website.pricelist_id

# ✅ Odoo 19
order = request.cart                  # current cart for this request
pricelist = request.pricelist         # current pricelist
# To create a fresh cart:
new_cart = request.website._create_cart()
```

This makes the cart lifecycle explicit and tied to the HTTP request rather than implicit on the website model.
