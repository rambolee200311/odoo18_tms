# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreateCustomerQuoteWizard(models.TransientModel):
    """Create a customer quote from the selected carrier inquiry."""

    _name = 'tlmp.create.customer.quote.wizard'
    _description = 'Create Customer Quote'

    request_id = fields.Many2one(
        'tlmp.transport.request', string='Request', required=True,
        default=lambda self: self.env.context.get('active_id'))
    inquiry_id = fields.Many2one(
        'tlmp.transport.inquiry', string='Source Inquiry', required=True,
        domain="[('request_id', '=', request_id), "
               "('state', '=', 'selected')]")
    carrier_id = fields.Many2one(
        'res.partner', string='Carrier',
        related='inquiry_id.partner_id', readonly=True)
    carrier_cost = fields.Monetary(
        string='Carrier Cost', related='inquiry_id.total_amount',
        readonly=True)
    margin_rate = fields.Float(
        string='Margin (%)',
        default=lambda self: float(
            self.env['ir.config_parameter'].sudo().get_param(
                'tlmp.service_margin_rate', default=0.15)) * 100)
    service_fee = fields.Monetary(string='Service Fee', default=0.0)
    customer_price = fields.Monetary(
        string='Customer Price', compute='_compute_customer_price')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='inquiry_id.currency_id', readonly=True)

    @api.depends('inquiry_id.total_amount', 'margin_rate', 'service_fee')
    def _compute_customer_price(self):
        for wizard in self:
            cost = wizard.inquiry_id.total_amount or 0.0
            wizard.customer_price = (
                cost * (1 + (wizard.margin_rate or 0.0) / 100.0)
                + (wizard.service_fee or 0.0))

    @api.onchange('request_id')
    def _onchange_request_id(self):
        if self.request_id and not self.inquiry_id:
            selected = self.request_id.inquiry_ids.filtered(
                lambda i: i.state == 'selected')[:1]
            self.inquiry_id = selected.id if selected else False

    def action_create(self):
        self.ensure_one()
        if not self.inquiry_id or self.inquiry_id.state != 'selected':
            raise UserError(_('Choose a selected carrier inquiry.'))
        if self.request_id.has_accepted_quote:
            raise UserError(_('This request already has an accepted quote.'))
        return self.inquiry_id.action_create_quote(
            margin_rate=self.margin_rate,
            service_fee=self.service_fee or 0.0)
