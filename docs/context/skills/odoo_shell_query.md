---
name: odoo-shell-query
description: Query Odoo database records by ID or domain using the Odoo shell. Use when the user asks to check, inspect, or verify data stored in the Odoo database, or to confirm field values, relationships, or record existence.
metadata:
  short-description: Inspect Odoo database records via shell
---

# Odoo Shell Query

## Method 1: Odoo Shell (Preferred — First Choice)

Use `echo` pipe to run non-interactive one-liners. This is the preferred method for all data queries.

### Syntax
```bash
echo "PYTHON_CODE" | /path/to/python /path/to/odoo-bin shell -c /path/to/odoo.conf -d DB_NAME
```

### Actual paths (Odoo18 TMS project)
```bash
echo "res = env['MODEL'].browse(ID); print(res.NAME, res.FIELD, ...)" | \
  /Users/lijianqiang/Documents/odoo18_tms/venv/bin/python \
  /Users/lijianqiang/Documents/odoo18_tms/odoo-bin shell \
  -c /Users/lijianqiang/Documents/odoo18_tms/odoo.conf \
  -d odoo18e_tms
```

**Important**: This requires `sandbox_permissions: require_escalated` — database access is sandboxed.

### Examples

#### Check a record
```python
res = env['tlmp.transport.request'].browse(1732)
print(f"ID={res.id} Name={res.name} State={res.state} Scene={res.scene_id.code if res.scene_id else 'NONE'}")
```

#### Check multiple records with domain
```python
recs = env['tlmp.transport.request'].search([('state', '=', 'draft')], limit=5)
for r in recs:
    print(r.id, r.name, r.state, r.scene_id.code if r.scene_id else '-')
```

#### Check if an action external ID exists
```python
import ast
entry = env['ir.model.data'].sudo().search([('module', '=', 'wd_tlms'), ('name', '=', 'action_tlmp_transport_scene')])
if entry:
    print(f"EXISTS: model={entry.model} res_id={entry.res_id}")
else:
    print("NOT FOUND")
```

## Method 2: psycopg2 Direct Query (Last Resort — Extreme Cases Only)

Only use when Odoo shell is genuinely unavailable. Odoo shell is always preferred.

```python
import psycopg2
conn = psycopg2.connect(host='127.0.0.1', port=5555, user='odoo', password='odoo', dbname='odoo18e_tms')
cur = conn.cursor()
cur.execute("SELECT id, name, state FROM tlmp_transport_request WHERE id = %s", [1732])
row = cur.fetchone()
conn.close()
```

## Common Table / Model Name Mappings

| Model (for shell) | Table (for raw SQL) |
|---|---|
| `tlmp.transport.request` | `tlmp_transport_request` |
| `tlmp.transport.order` | `tlmp_transport_order` |
| `tlmp.transport.scene` | `tlmp_transport_scene` |
| `pickup.plan` | `pickup_plan` |
| `res.partner` | `res_partner` |
| `stock.warehouse` | `stock_warehouse` |
| `ir.model.data` | `ir_model_data` |

## Quick Reference: Odoo ORM Shell

### Browse by ID
`env['model'].browse(id)` → single record

### Search by domain
`env['model'].search([('field', 'operator', value)])` → recordset

### Read fields
`record.field_name` → field value (including related/Many2one)

### Related fields (Many2one)
`record.scene_id.code` → follow the relation

### One2many / inverse
`record.line_ids` → recordset of lines
`len(record.line_ids)` → count

### Check if record exists
`env['model'].search_count([('field', '=', 'value')])` → integer

### Check external ID
`env.ref('module.xml_id')` → record or raise ValueError
