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

    carrier_cost = fields.Monetary(string='Carrier Cost',
        help='Cost from the carrier (from accepted inquiry).')
    margin_amount = fields.Monetary(string='Margin Amount (markup)',
        help='Manual markup on top of carrier cost.')
    margin_rate = fields.Float(string='Margin Rate (%)', compute='_compute_margin_rate', store=True,
        help='Calculated as margin_amount / carrier_cost * 100.')
    fee_line_ids = fields.One2many('transport.fee.line', 'source_quote_id',
        string='Fee Lines', copy=False)

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

    @api.depends('carrier_cost', 'margin_amount')
    def _compute_margin_rate(self):
        for r in self:
            r.margin_rate = (r.margin_amount / r.carrier_cost * 100) if r.carrier_cost else 0.0
        for r in self:
            r.total_base_fee = sum(r.line_ids.mapped('subtotal'))
            r.total_surcharge = 0.0
            r.total_amount = r.total_base_fee + r.total_surcharge

    def action_accept(self):
        self.ensure_one()
        if self.state != 'sent':
            raise UserError(_('Only sent quotes can be accepted.'))
        self.write({'state': 'accepted'})
        self._auto_create_order()
        return True

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
            'scene_id': self.request_id.scene_id.id if self.request_id and self.request_id.scene_id else False,
            # Sprint44: copy address from request
            'origin_street': self.request_id.origin_street if self.request_id else False,
            'origin_zip': self.request_id.origin_zip if self.request_id else False,
            'origin_city': self.request_id.origin_city if self.request_id else False,
            'origin_state_id': self.request_id.origin_state_id.id if self.request_id and self.request_id.origin_state_id else False,
            'origin_country_id': self.request_id.origin_country_id.id if self.request_id and self.request_id.origin_country_id else False,
            'destination_street': self.request_id.destination_street if self.request_id else False,
            'destination_zip': self.request_id.destination_zip if self.request_id else False,
            'destination_city': self.request_id.destination_city if self.request_id else False,
            'destination_state_id': self.request_id.destination_state_id.id if self.request_id and self.request_id.destination_state_id else False,
            'destination_country_id': self.request_id.destination_country_id.id if self.request_id and self.request_id.destination_country_id else False,
            'request_id': self.request_id.id,
            'quote_id': self.id,
            'inquiry_id': self.inquiry_id.id,
            'partner_id': self.partner_id.id,
            'transport_type_id': self.request_id.transport_type_id.id if self.request_id and self.request_id.transport_type_id else False,
            'fleet_operation_mode': 'subcontracted',
            'total_customer_charge': self.total_amount,
            'source_amount_customer': self.total_amount,
            'carrier_id': self.partner_id.id,
            'price_source': 'quote',
        })
        # Auto-create fee lines
        charge_item = self.env['world.depot.charge.item'].search([], limit=1)
        if charge_item:
            FeeLine = self.env['transport.fee.line']
            if self.partner_id:
                FeeLine.create({
                    'fee_type_id': charge_item.id, 'source_type': 'commercial',
                    'source_quote_id': self.id, 'party_type': 'customer_charge',
                    'partner_id': self.partner_id.id,
                    'unit_amount': self.total_amount, 'quantity': 1.0,
                    'description': self.name or 'Transport charge'})
            inquiry_partner = self.inquiry_id.partner_id if self.inquiry_id else False
            if inquiry_partner and (self.carrier_cost or 0.0) > 0:
                FeeLine.create({
                    'fee_type_id': charge_item.id, 'source_type': 'commercial',
                    'source_quote_id': self.id, 'party_type': 'carrier_cost',
                    'partner_id': inquiry_partner.id,
                    'unit_amount': self.carrier_cost, 'quantity': 1.0,
                    'description': (self.name or '') + ' (carrier)'})
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
