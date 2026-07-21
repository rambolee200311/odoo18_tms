# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class BlContainer(models.Model):
    _name = 'bl.container'
    _description = 'Container'
    _order = 'id desc'

    bl_no = fields.Char(string='BL No.', index=True)
    container_no = fields.Char(string='Container No.', required=True, index=True)
    container_type = fields.Selection([
        ('20GP', '20GP'), ('40GP', '40GP'), ('40HQ', '40HQ'),
        ('40HC', '40HC'), ('45HQ', '45HQ'), ('OT', 'OT'),
        ('FR', 'FR'), ('RF', 'RF'), ('other', 'Other'),
    ], string='Container Type', default='20GP')
    supplier = fields.Char(string='Supplier')
    destination_warehouse = fields.Many2one('stock.warehouse', string='Destination Warehouse')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')
    plan_ids = fields.One2many('container.transport.plan', 'container_id', string='Schedule Records')
    scheduled = fields.Boolean(string='Scheduled', compute='_compute_scheduled', store=True)

    @api.depends('state')
    def _compute_scheduled(self):
        for r in self:
            r.scheduled = r.state == 'scheduled'

    def get_unplanned_containers(self):
        # Sync from pickup.plan.container.line (pickup plans)
        lines = self.env['pickup.plan.container.line'].search([
            ('container_number', '!=', False)
        ])
        for line in lines:
            existing = self.search([('container_no', '=', line.container_number)], limit=1)
            if not existing:
                plan = line.plan_id
                self.create({
                    'container_no': line.container_number,
                    'container_type': line.container_type or '20GP',
                    'bl_no': line.bl_number or '',
                    'destination_warehouse': plan.warehouse_id.id if plan and plan.warehouse_id else False,
                    'state': 'pending',
                })
        return self.search_read([('state', '!=', 'scheduled')],
            ['id', 'bl_no', 'container_no', 'container_type',
             'supplier', 'destination_warehouse', 'state', 'scheduled'])


class TransportPlan(models.Model):
    _name = 'container.transport.plan'
    _description = 'Transport Schedule Record'
    _order = 'plan_date desc, id desc'

    plan_date = fields.Date(string='Plan Date', required=True, index=True)
    container_id = fields.Many2one('bl.container', string='Container', required=True, ondelete='cascade')
    container_no = fields.Char(string='Container No.', related='container_id.container_no', store=True, readonly=True)
    bl_no = fields.Char(string='BL No.', related='container_id.bl_no', store=True, readonly=True)
    transport_company = fields.Char(string='Trucking Company')
    remark = fields.Text(string='Remark')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    def create_transport_plan(self, container_id, plan_date):
        container = self.env['bl.container'].browse(container_id)
        if not container:
            raise UserError('Container not found')
        plan = self.create({
            'plan_date': plan_date,
            'container_id': container_id,
            'state': 'draft',
        })
        container.write({'state': 'scheduled'})
        return plan.read(['id', 'plan_date', 'container_id', 'container_no', 'bl_no', 'state'])

    def delete_transport_plan(self, plan_id):
        plan = self.browse(plan_id)
        if not plan:
            return False
        container = plan.container_id
        plan.unlink()
        if container:
            other = self.search([('container_id', '=', container.id)], limit=1)
            if not other:
                container.write({'state': 'pending'})
        return True

    def update_transport_plan(self, plan_id, vals):
        plan = self.browse(plan_id)
        if not plan:
            raise UserError('Plan not found')
        plan.write(vals)
        return plan.read(['id', 'plan_date', 'container_id', 'container_no', 'bl_no', 'state'])

    def get_daily_plan_summary(self, start_date, end_date):
        plans = self.search_read([
            ('plan_date', '>=', start_date),
            ('plan_date', '<=', end_date),
        ], ['id', 'plan_date', 'container_id', 'container_no', 'bl_no', 'state'])
        result = {}
        for p in plans:
            ds = str(p['plan_date'])
            if ds not in result:
                result[ds] = {'count': 0, 'containers': []}
            result[ds]['count'] += 1
            result[ds]['containers'].append(p)
        return result
