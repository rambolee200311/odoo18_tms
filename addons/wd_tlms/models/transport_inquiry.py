# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class TransportInquiry(models.Model):
    _name = 'tlmp.transport.inquiry'
    _description = 'Transport Inquiry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Inquiry No.', required=True, copy=False,
                       default=lambda self: _('New'))
    request_id = fields.Many2one('tlmp.transport.request', string='Request')
    partner_id = fields.Many2one('res.partner', string='Carrier', required=True)
    from_location_text = fields.Text(string='From')
    to_location_text = fields.Text(string='To')
    cargo_summary = fields.Text(string='Cargo')
    weight_kg = fields.Float(string='Weight (kg)')
    volume_m3 = fields.Float(string='Volume (m3)')
    pickup_date = fields.Datetime(string='Pickup Date')
    delivery_deadline = fields.Datetime(string='Delivery Deadline')
    line_ids = fields.One2many('tlmp.transport.inquiry.line', 'inquiry_id',
                               string='Inquiry Lines')
    total_amount = fields.Monetary(string='Total', compute='_compute_total', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    response_date = fields.Datetime(string='Response Date')
    validity_date = fields.Date(string='Valid Until')
    carrier_notes = fields.Text(string='Carrier Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('responded', 'Responded'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)
    sent_date = fields.Datetime(string='Sent Date')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('tlmp.inquiry.seq') or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for r in self:
            r.total_amount = sum(r.line_ids.mapped('subtotal'))

    def action_send(self):
        self.write({'state': 'sent', 'sent_date': fields.Datetime.now()})
        return True

    def action_respond(self):
        self.write({'state': 'responded', 'response_date': fields.Datetime.now()})
        return True

    def action_accept(self):
        self.write({'state': 'accepted'})
        return True

    def action_reject(self, reason=None):
        self.write({'state': 'rejected'})
        return True

    def _cron_expire(self):
        expired = self.search([('state', '=', 'sent'),
                               ('validity_date', '<', date.today())])
        expired.write({'state': 'expired'})
        return True


class TransportInquiryLine(models.Model):
    _name = 'tlmp.transport.inquiry.line'
    _description = 'Inquiry Line'

    inquiry_id = fields.Many2one('tlmp.transport.inquiry', string='Inquiry', required=True,
                                 ondelete='cascade')
    description = fields.Char(string='Description', required=True)
    unit_price = fields.Monetary(string='Unit Price')
    quantity = fields.Float(string='Quantity', default=1.0)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    currency_id = fields.Many2one('res.currency', related='inquiry_id.currency_id')

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for r in self:
            r.subtotal = (r.unit_price or 0.0) * r.quantity
