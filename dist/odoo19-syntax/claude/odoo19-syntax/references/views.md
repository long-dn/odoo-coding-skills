# Odoo 19 — XML Views Reference

This reference covers all XML view changes: form, list (formerly tree), kanban, search, QWeb templates, chatter.

## Table of contents
1. `attrs` and `states` — fully removed, use inline expressions
2. `<tree>` → `<list>`
3. Kanban templates — `kanban-card` → `card`
4. `t-raw` removed, `t-esc` removed, `t-call` new syntax — use `t-out`
5. Chatter shorthand `<chatter/>`
6. `column_invisible` syntax
7. XPath updates for inherited views
8. Search view — `<group>` cannot have `string` or `expand`
9. Complete migrated form view example

---

## 1. `attrs` and `states` — fully removed (gone since Odoo 17)

The `attrs="{...}"` dict-in-XML pattern was removed in Odoo 17 and stays removed in 18, 19. Same for the `states="..."` shorthand on buttons/fields. Use inline boolean expressions on `invisible`, `readonly`, `required`, `column_invisible`.

```xml
<!-- ❌ OLD -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly':  [('state', 'not in', ['draft', 'sent'])],
               'required':  [('state', '=', 'confirmed')]}" />

<button name="action_confirm"
        states="draft"
        type="object" string="Confirm"/>

<!-- ✅ Odoo 19 -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state not in ('draft', 'sent')"
       required="state == 'confirmed'" />

<button name="action_confirm"
        invisible="state != 'draft'"
        type="object" string="Confirm"/>
```

### Expression syntax cheat-sheet

```xml
<!-- equality -->
<field name="x" invisible="state == 'draft'"/>

<!-- not equal -->
<field name="x" invisible="state != 'sale'"/>

<!-- in / not in -->
<field name="x" invisible="state in ('draft', 'cancel')"/>
<field name="x" invisible="state not in ('sale', 'done')"/>

<!-- boolean -->
<field name="x" invisible="not active"/>
<field name="x" invisible="active"/>

<!-- AND -->
<field name="x" invisible="state == 'draft' and type == 'service'"/>

<!-- OR -->
<field name="x" invisible="type == 'service' or not active"/>

<!-- numeric -->
<field name="x" readonly="qty_invoiced &gt; 0"/>
<!-- (use &gt; / &lt; in XML, or wrap in CDATA) -->

<!-- nested -->
<field name="x" invisible="(state == 'draft' and not partner_id) or state == 'cancel'"/>
```

These expressions evaluate in a JavaScript-like context: no Python imports, no function calls, just comparisons and logical operators. For complex logic, add a Boolean computed field on the model.

### Pitfall: inverted `states`

`states="draft"` meant **visible when state is draft**. The inline equivalent is `invisible="state != 'draft'"`. `states="draft,sent"` → `invisible="state not in ('draft', 'sent')"`. Drop a `not` and the element vanishes.

## 2. `<tree>` → `<list>`

Tree views are now list views. Rename the tag everywhere — view definition AND inherited XPath targets.

```xml
<!-- ❌ OLD -->
<tree string="Sale Orders" decoration-danger="state == 'cancel'">
    <field name="name"/>
    <field name="state"/>
</tree>

<!-- ✅ Odoo 19 -->
<list string="Sale Orders" decoration-danger="state == 'cancel'">
    <field name="name"/>
    <field name="state"/>
</list>
```

Inherited views:

```xml
<!-- ❌ OLD XPath -->
<xpath expr="//field[@name='order_line']/tree/field[@name='price_unit']" position="after">

<!-- ✅ Odoo 19 -->
<xpath expr="//field[@name='order_line']/list/field[@name='price_unit']" position="after">
```

The view type in `ir.actions.act_window` records is also `list` (not `tree`):

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="view_mode">list,form</field>   <!-- not "tree,form" -->
</record>
```

## 3. Kanban templates — `kanban-card` → `card`

The kanban template name changed and the structure was simplified. Use `<header>`, `<main>`, `<footer>` semantic blocks instead of nested divs.

```xml
<!-- ❌ OLD -->
<kanban>
    <templates>
        <t t-name="kanban-card">
            <div class="oe_kanban_card oe_kanban_global_click">
                <div class="o_kanban_record_top">
                    <strong><field name="name"/></strong>
                </div>
                <div class="o_kanban_record_bottom">
                    <field name="priority" widget="priority"/>
                    <field name="user_id" widget="many2one_avatar_user"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>

<!-- ✅ Odoo 19 -->
<kanban>
    <templates>
        <t t-name="card">
            <field name="name" class="fw-bold"/>
            <footer>
                <field name="priority" widget="priority"/>
                <field name="user_id" widget="many2one_avatar_user" class="ms-auto"/>
            </footer>
        </t>
    </templates>
</kanban>
```

## 4. `t-raw` removed, `t-esc` removed → use `t-out`

`t-raw` was removed in Odoo 17 (XSS risk). `t-esc` was deprecated in 17/18 and is **fully removed in Odoo 19** — using it raises a template error. The single replacement for both is `t-out`, which auto-escapes plain strings and renders `Markup()` objects as HTML.

```xml
<!-- ❌ OLD / fails in Odoo 19 -->
<div t-raw="record.description"/>
<span t-esc="record.name"/>

<!-- ✅ Odoo 19 — t-out for everything -->
<div t-out="record.description"/>
<span t-out="record.name"/>
```

If you genuinely need to render raw HTML from a controlled Python source, return a `Markup()` object from Python — `t-out` will render it as HTML. Plain strings always get escaped.

### `t-call` new attribute syntax

Odoo 19 prefers attribute-based parameter passing for `t-call`, replacing the older `t-set` block approach. Both still work for now, but the new form is cleaner and the documented standard going forward.

```xml
<!-- ❌ OLD (still works, but messier) -->
<t t-call="my_module.my_template">
    <t t-set="custom_value" t-value="x + y"/>
    <t t-set="title" t-value="'Hello'"/>
</t>

<!-- ✅ Odoo 19 — preferred -->
<t t-call="my_module.my_template" custom_value="x + y" title="'Hello'"/>
```

Inside the called template, the values are accessed the same way (as variables in the rendering context).

## 5. Chatter shorthand `<chatter/>`

Replace the verbose three-field chatter boilerplate with `<chatter/>`.

```xml
<!-- ❌ OLD -->
<div class="oe_chatter">
    <field name="message_follower_ids" widget="mail_followers"/>
    <field name="activity_ids" widget="mail_activity"/>
    <field name="message_ids" widget="mail_thread"/>
</div>

<!-- ✅ Odoo 19 -->
<chatter/>
```

## 6. `column_invisible` syntax inside O2M sub-views

When you want a column hidden inside an embedded list view based on the parent record's state, use `column_invisible` with the `parent.` prefix in an inline expression:

```xml
<!-- ✅ Odoo 19 -->
<field name="order_line">
    <list editable="bottom">
        <field name="product_id"/>
        <field name="qty_delivered"
               column_invisible="parent.state == 'draft'"/>
    </list>
</field>
```

## 7. XPath updates for inherited views

When inheriting from core views or your own older views, audit every XPath:
- `tree` → `list` (in expressions targeting the tag).
- Avoid targeting `attrs` attributes — they no longer exist; target the new inline attributes (`invisible`, `readonly`, `required`).
- Avoid targeting the old chatter divs if the parent moved to `<chatter/>`.

## 8. Search view — `<group>` cannot have `string` or `expand` attributes

In Odoo 19 search views, the `<group>` element used to wrap "Group By" filters does NOT accept `string` OR `expand` attributes. Both `<group string="Group By">` and `<group expand="0">` patterns from older versions are removed. Leave the tag bare.

```xml
<!-- ❌ OLD / breaks in Odoo 19 -->
<search>
    <field name="name"/>
    <filter name="my_filter" string="Mine" domain="[('user_id', '=', uid)]"/>
    <group expand="0" string="Group By">
        <filter name="group_by_state" string="State" context="{'group_by': 'state'}"/>
        <filter name="group_by_user" string="User" context="{'group_by': 'user_id'}"/>
    </group>
</search>

<!-- ✅ Odoo 19 — bare <group>, no string, no expand -->
<search>
    <field name="name"/>
    <filter name="my_filter" string="Mine" domain="[('user_id', '=', uid)]"/>
    <group>
        <filter name="group_by_state" string="State" context="{'group_by': 'state'}"/>
        <filter name="group_by_user" string="User" context="{'group_by': 'user_id'}"/>
    </group>
</search>
```

The "Group By" label is provided by the framework automatically. Both attributes were legacy holdovers.

This rule is **specific to search views**. In form views and other contexts, `<group string="...">` is still valid and renders as a section header.

## 9. Complete migrated form view

```xml
<!-- ✅ Odoo 19 form view, fully migrated -->
<form string="Sale Order">
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                invisible="state != 'draft'"/>
        <button name="action_cancel" type="object" string="Cancel"
                invisible="state in ('cancel', 'done')"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,sale,done"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name" readonly="state != 'draft'"/></h1>
        </div>
        <group>
            <group>
                <field name="partner_id"
                       readonly="state not in ('draft', 'sent')"/>
                <field name="date_order"
                       required="state == 'sale'"/>
            </group>
            <group>
                <field name="warehouse_id"
                       invisible="picking_policy == 'direct'"/>
            </group>
        </group>
        <notebook>
            <page string="Order Lines">
                <field name="order_line"
                       readonly="state in ('done', 'cancel')">
                    <list editable="bottom">
                        <field name="product_id"/>
                        <field name="qty_delivered"
                               column_invisible="parent.state == 'draft'"/>
                    </list>
                </field>
            </page>
        </notebook>
    </sheet>
    <chatter/>
</form>
```
