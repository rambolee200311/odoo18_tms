# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TransportRequest(models.Model):
    _name = 'tlmp.transport.request'
    _description = 'Transport Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Request No.', required=True, copy=False,
                       default=lambda self: _('New'))
    transport_type = fields.Selection([
        ('port_to_warehouse', 'Port to Warehouse'),
        ('to_customer', 'To Customer'),
        ('pickup_to_warehouse', 'Pickup to Warehouse'),
        ('warehouse_transfer', 'Warehouse Transfer'),
        ('reverse_logistics', 'Reverse Logistics'),
    ], string='Transport Type', required=True, default='to_customer')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    customer_ref = fields.Char(string='Customer Reference')
    contact_person = fields.Char(string='Contact Person')
    contact_phone = fields.Char(string='Contact Phone')
    contact_email = fields.Char(string='Contact Email')
    pickup_location_id = fields.Many2one('res.partner', string='Pickup Location', required=True)
    delivery_location_id = fields.Many2one('res.partner', string='Delivery Location', required=True)
    cargo_description = fields.Text(string='Cargo Description')
    cargo_weight = fields.Float(string='Weight (kg)', digits='Stock Weight')
    cargo_volume = fields.Float(string='Volume (m3)', digits='Volume')
    pallet_count = fields.Integer(string='Pallets')
    package_count = fields.Integer(string='Packages')
    requested_pickup_date = fields.Datetime(string='Requested Pickup')
    requested_delivery_date = fields.Datetime(string='Requested Delivery')
    special_requirements = fields.Text(string='Special Requirements')
    has_dangerous_goods = fields.Boolean(string='Dangerous Goods', default=False)
    customs_declaration_ref = fields.Char(string='Customs Decl. Ref.')
    wms_transfer_order_ref = fields.Char(string='WMS Transfer Ref.')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('tlmp.request.seq') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True
    
    def action_reject(self, reason=None):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Only confirmed requests can be rejected.'))
        self.write({'state': 'draft'})
        return True
