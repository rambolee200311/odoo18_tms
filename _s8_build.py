import os
d = '/Users/lijianqiang/Documents/odoo18_tms/addons/wd_tlms'

# ============================================================
# 1) schedule_plan.py — add pickup_plan_id field
# ============================================================
fp = os.path.join(d, 'models/schedule_plan.py')
with open(fp) as f:
    c = f.read()
old_cl = "    container_line_id = fields.Many2one("
new_cl = '    pickup_plan_id = fields.Many2one(\n'
new_cl += "        'pickup.plan', string='Pickup Plan',\n"
new_cl += '        ondelete='set null', index=True,\n'
new_cl += "        help='Pickup plan created from this schedule record.')\n\n"
new_cl += old_cl
c = c.replace(old_cl, new_cl)
with open(fp, 'w') as f:
    f.write(c)
print('OK: schedule_plan.py (+pickup_plan_id)')

# ============================================================
# 2) pickup_plan_fix.py — extend action_create_transport_order for fee.line
# ============================================================
fp = os.path.join(d, 'models/pickup_plan_fix.py')
with open(fp) as f:
    c = f.read()

# After the container loop and before self.transport_order_id = order.id
# Insert fee.line creation
old_fee = '            })\n        self.transport_order_id = order.id'
new_fee = '''            })

        # Create fee.line (carrier cost) for plan-driven flow
        charge_item = self.env['world.depot.charge.item'].search([], limit=1)
        if charge_item and self.carrier_id:
            self.env['transport.fee.line'].create({
                'fee_type_id': charge_item.id,
                'source_type': 'plan_driven',
                'source_order_id': order.id,
                'party_type': 'carrier_cost',
                'partner_id': self.carrier_id.id,
                'quantity': 1.0,
                'unit_amount': 0.0,
                'description': _('Transport cost - %s') % self.name,
            })
        self.transport_order_id = order.id'''
c = c.replace(old_fee, new_fee)

with open(fp, 'w') as f:
    f.write(c)
print('OK: pickup_plan_fix.py (+fee.line on order creation)')

# ============================================================
# 3) transport_request_views.xml — enhance Scheduling tab
# ============================================================
fp = os.path.join(d, 'views/transport_request_views.xml')
with open(fp) as f:
    c = f.read()

# Add schedule.plan.schedule sub-list after pickup_plans
old_sp = '''                            <group string="Pickup Plans">
                                <field name="pickup_plan_ids" readonly="1">
                                    <list>
                                        <field name="name"/>
                                        <field name="cargo_type"/>
                                        <field name="scheduled_date"/>
                                    </list>
                                </field>
                            </group>'''
new_sp = '''                            <group string="Pickup Plans">
                                <field name="pickup_plan_ids" readonly="1">
                                    <list>
                                        <field name="name"/>
                                        <field name="cargo_type"/>
                                        <field name="scheduled_date"/>
                                    </list>
                                </field>
                            </group>
                            <group string="Schedule Plans" colspan="2">
                                <field name="schedule_ids" readonly="1">
                                    <list>
                                        <field name="plan_id"/>
                                        <field name="scheduled_date"/>
                                        <field name="cargo_type"/>
                                        <field name="container_line_id"/>
                                        <field name="state" widget="badge"/>
                                    </list>
                                </field>
                            </group>'''
c = c.replace(old_sp, new_sp)

with open(fp, 'w') as f:
    f.write(c)
print('OK: transport_request_views.xml (+schedule plans sub-list)')

# ============================================================
# 4) schedule_calendar_views.xml — add schedule.plan.schedule form/tree
# ============================================================
# The existing views already have calendar/tree/form/search for schedule.plan.schedule
# No changes needed.
print('OK: schedule_calendar_views.xml (no changes needed)')

print()
print('Sprint8 build complete')
print('Changes:')
print('  - schedule_plan.py: +pickup_plan_id')
print('  - pickup_plan_fix.py: action_create_transport_order +fee.line')
print('  - transport_request_views.xml: +Schedule Plans sub-list')
