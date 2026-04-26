# Test Case 2: Migrate XML form view to Odoo 19

## User Prompt

I have this form view from an old Odoo module. The project I'm putting it into is Odoo 19. Please update the syntax so it works:

```xml
<form string="Project Task">
    <header>
        <button name="action_start" type="object" string="Start"
                states="draft" />
        <button name="action_done" type="object" string="Mark Done"
                attrs="{'invisible': [('state', 'not in', ['in_progress'])]}"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="name"
                   attrs="{'readonly': [('state', '=', 'done')]}"/>
            <field name="description"
                   attrs="{'invisible': [('state', '=', 'draft')]}"/>
            <field name="user_id"
                   attrs="{'required': [('state', '=', 'in_progress')]}"/>
        </group>
        <notebook>
            <page string="Subtasks">
                <field name="subtask_ids">
                    <tree editable="bottom">
                        <field name="name"/>
                        <field name="done"
                               attrs="{'column_invisible': [('parent.state', '=', 'draft')]}"/>
                    </tree>
                </field>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids" widget="mail_followers"/>
        <field name="activity_ids" widget="mail_activity"/>
        <field name="message_ids" widget="mail_thread"/>
    </div>
</form>
```

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'`.

## What we're testing

- Does Claude detect Odoo 19?
- `attrs="..."` → inline `invisible=`, `readonly=`, `required=`.
- `states="draft"` → `invisible="state != 'draft'"` (correct inversion!).
- `<tree>` → `<list>`.
- `column_invisible` with `parent.` prefix as inline expression.
- Three-field chatter → `<chatter/>`.

## Expected output

A migrated form view with:
- No `attrs=` anywhere.
- No `states=` anywhere.
- `<list>` instead of `<tree>`.
- `<chatter/>` shorthand.
- Correctly inverted boolean expressions (the `states="draft"` button should now be `invisible="state != 'draft'"`).
