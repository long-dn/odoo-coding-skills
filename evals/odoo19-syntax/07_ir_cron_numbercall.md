# Test Case 7: ir.cron data record in Odoo 19

## User Prompt

In my Odoo 19 module, please create a scheduled action (ir.cron) that runs the method `cleanup_old_logs()` on `library.book.log` every day. It should run continuously (no expiration).

## Project context

`__manifest__.py` has `'version': '19.0.1.0.0'`.

## What we're testing

- Does Claude know that `numbercall` field has been removed from `ir.cron` in Odoo 19?
- Does Claude omit `<field name="numbercall">` entirely?
- Bonus: Claude should use `interval_number` and `interval_type` to set the schedule.

## Expected output

XML data file (e.g., `data/cron.xml`) with an `ir.cron` record. Key elements:

- `<field name="model_id" ref="..."/>`
- `<field name="state">code</field>`
- `<field name="code">model.cleanup_old_logs()</field>`
- `<field name="interval_number">1</field>`
- `<field name="interval_type">days</field>`
- **NO** `<field name="numbercall">` line.

## Anti-patterns to flag

- Including `<field name="numbercall">-1</field>` or any other numbercall value.
- Mentioning numbercall in the explanation as if it still works.
