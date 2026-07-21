# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class TransportQuote(models.Model):
    _name = 'tlmp.transport.quote'
    _description = 'Transport Quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Quote No.', required=True, copy=False,
                       default=lambda self: _('New'))
    request_id = fields.Many2one('tlmp.transport.request', string='Request')
    inquiry_id = fields.Many2one('tlmp.transport.inquiry', string='Inquiry')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    transport_mode = fields.Selection([('road', 'Road'), ('multimodal', 'Multimodal')],
                                      default='road')
    line_ids = fields.One2many('tlmp.transport.quote.line', 'quote_id', string='Lines')
    total_base_fee = fields.Monetary(string='Base Fee', compute='_compute_total', store=True)
    total_surcharge = fields.Monetary(string='Surcharge', compute='_compute_total', store=True)
    total_amount = fields.Monetary(string='Total', compute='_compute_total', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    validity_date = fields.Date(string='Valid Until')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('tlmp.quote.seq') or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for r in self:
            r.total_base_fee = sum(r.line_ids.mapped('subtotal'))
            r.total_surcharge = 0.0
            r.total_amount = r.total_base_fee + r.total_surcharge

    def action_send(self):
        self.write({'state': 'sent'})
        return True

    def action_accept_from_portal(self):
        self.ensure_one()
        if self.state != 'sent':
            raise UserError(_('Quote is not in sent state.'))
        if self.validity_date and self.validity_date < fields.Date.today():
            self.write({'state': 'expired'})
            raise UserError(_('Quote has expired. Please request a new quote.'))
        self.write({'state': 'accepted'})
        self._auto_create_order()
        return True

    def action_cancel(self, reason=None):
        self.write({'state': 'cancelled'})
        return True

    def action_reject(self, reason=None):
        self.write({'state': 'rejected'})
        # Return inquiry to 'sent' state for re-quoting
        if self.inquiry_id and self.inquiry_id.state == 'accepted':
            self.inquiry_id.write({'state': 'sent', 'response_date': False})
        return True

    def _auto_create_order(self):
        self.ensure_one()
        order = self.env['tlmp.transport.order'].create({
            'request_id': self.request_id.id,
            'quote_id': self.id,
            'inquiry_id': self.inquiry_id.id,
            'partner_id': self.partner_id.id,
            'transport_type': self.request_id.transport_type if self.request_id else 'to_customer',
            'fleet_operation_mode': 'subcontracted',
            'total_customer_charge': self.total_amount,
            'source_amount_customer': self.total_amount,
            'price_source': 'quote',
        })
        return order

    def _cron_expire(self):
        expired = self.search([('state', '=', 'sent'),
                               ('validity_date', '<', fields.Date.today())])
        expired.write({'state': 'expired'})
        return True


class TransportQuoteLine(models.Model):
    _name = 'tlmp.transport.quote.line'
    _description = 'Quote Line'

    quote_id = fields.Many2one('tlmp.transport.quote', string='Quote', required=True,
                               ondelete='cascade')
    description = fields.Char(string='Description', required=True)
    unit_price = fields.Monetary(string='Unit Price')
    quantity = fields.Float(string='Quantity', default=1.0)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    currency_id = fields.Many2one('res.currency', related='quote_id.currency_id')

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for r in self:
            r.subtotal = (r.unit_price or 0.0) * r.quantity
