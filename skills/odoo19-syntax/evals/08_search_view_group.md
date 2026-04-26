# Test Case 8: Search view with group filters in Odoo 19

## User Prompt

In my Odoo 19 module, create a search view for `library.book` that:
- Has a search field on `name`
- Has a filter "Available" filtering on `available == True`
- Has Group By options for `author_id` and `category_id`

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'`.

## What we're testing

- Does Claude know that `<group>` inside a `<search>` view CANNOT have a `string` attribute in Odoo 19?
- Does the output use `<group>` (empty, no `string="Group By"`) wrapping the group_by filters?
- Does Claude avoid the older `<group expand="0" string="Group By">` pattern?

## Expected output

A search view definition like:

```xml
<record id="view_library_book_search" model="ir.ui.view">
    <field name="name">library.book.search</field>
    <field name="model">library.book</field>
    <field name="arch" type="xml">
        <search>
            <field name="name"/>
            <filter name="available" string="Available" domain="[('available', '=', True)]"/>
            <group>
                <filter name="group_by_author" string="Author"
                        context="{'group_by': 'author_id'}"/>
                <filter name="group_by_category" string="Category"
                        context="{'group_by': 'category_id'}"/>
            </group>
        </search>
    </field>
</record>
```

The key thing: `<group>` is bare — no `string=` attribute, no `expand=` attribute.

## Anti-patterns to flag

- `<group string="Group By">` (string attr is invalid here in Odoo 19).
- `<group expand="0" string="Group By">` (both attrs unnecessary/invalid).
