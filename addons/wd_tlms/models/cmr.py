# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CMR(models.Model):
    _name = 'tlmp.cmr'
    _description = 'CMR Waybill'
    _rec_name = 'cmr_number'

    name = fields.Char(string='CMR Ref.', required=True, copy=False,
                       default=lambda self: _('New'))
    order_id = fields.Many2one('tlmp.transport.order', string='Transport Order', required=True)
    cmr_number = fields.Char(string='CMR Number', required=True, index=True)
    copy_number = fields.Selection([
        ('1', 'Copy 1 - Sender'),
        ('2', 'Copy 2 - Carrier'),
        ('3', 'Copy 3 - Consignee'),
        ('4', 'Copy 4 - Extra'),
    ], string='Copy', required=True, default='1')
    sender_id = fields.Many2one('res.partner', string='Sender', required=True)
    consignee_id = fields.Many2one('res.partner', string='Consignee', required=True)
    place_of_taking_over = fields.Char(string='Place of Taking Over')
    place_of_delivery = fields.Char(string='Place of Delivery')
    carrier_id = fields.Many2one('res.partner', string='Carrier', required=True)
    vehicle_reg_no = fields.Char(string='Vehicle Reg. No.')
    packages_count = fields.Integer(string='Packages')
    gross_weight = fields.Float(string='Gross Weight (kg)')
    volume_m3 = fields.Float(string='Volume (m3)')
    cargo_description = fields.Text(string='Cargo Description')
    container_no = fields.Char(string='Container No.')
    seal_no = fields.Char(string='Seal No.')
    has_dangerous_goods = fields.Boolean(related='order_id.has_dangerous_goods')
    adr_class = fields.Char(related='order_id.adr_class')
    adr_un_number = fields.Char(related='order_id.adr_un_number')
    freight_charges = fields.Monetary(string='Freight Charges')
    additional_charges = fields.Monetary(string='Additional Charges')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    sender_remarks = fields.Text(string='Sender Remarks')
    carrier_remarks = fields.Text(string='Carrier Remarks')
    sender_instructions = fields.Text(string='Sender Instructions')
    documents_attached = fields.Text(string='Documents Attached')
    pickup_datetime = fields.Datetime(string='Pickup Date')
    delivery_datetime = fields.Datetime(string='Delivery Date')
    damage_description = fields.Text(string='Reservations')
    signed_by = fields.Char(string='Signed By')
    signed_date = fields.Datetime(string='Signed Date')
    signature_image = fields.Binary(string='Signature', attachment=True)
    signed_cmr_pdf = fields.Binary(string='Signed CMR PDF', attachment=True)
    language = fields.Selection([('en', 'English'), ('nl', 'Nederlands')],
                                string='Language', default='en')
    is_pod_confirmed = fields.Boolean(string='POD Confirmed', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('printed', 'Printed'),
        ('in_transit', 'In Transit'),
        ('signed', 'Signed'),
        ('archived', 'Archived'),
    ], string='Status', default='draft')

    _sql_constraints = [
        ('cmr_copy_unique', 'unique(cmr_number, copy_number)',
         'CMR number + copy must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('tlmp.cmr.seq') or _('New')
        return super().create(vals_list)

    def action_print_cmr(self):
        return self.env.ref('wd_tlms.report_cmr').report_action(self)

    def action_confirm_signature(self):
        self.write({'state': 'signed', 'is_pod_confirmed': True})
        return True

    def action_archive(self):
        self.write({'state': 'archived'})
        return True

