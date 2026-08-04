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
    partner_id = fields.Many2one('res.partner', string='Carrier')
    from_location_text = fields.Text(string='From (deprecated, use related address fields)', help='Legacy text field. Structured address is projected from request_id.')
    to_location_text = fields.Text(string='To (deprecated, use related address fields)', help='Legacy text field. Structured address is projected from request_id.')

    # Sprint45: related address projection from request (single source of truth)
    origin_street = fields.Char(related='request_id.origin_street', string='Origin Street', readonly=True)
    origin_zip = fields.Char(related='request_id.origin_zip', string='Origin Zip', readonly=True)
    origin_city = fields.Char(related='request_id.origin_city', string='Origin City', readonly=True)
    origin_state_id = fields.Many2one(related='request_id.origin_state_id', string='Origin State', readonly=True)
    origin_country_id = fields.Many2one(related='request_id.origin_country_id', string='Origin Country', readonly=True)
    destination_street = fields.Char(related='request_id.destination_street', string='Destination Street', readonly=True)
    destination_zip = fields.Char(related='request_id.destination_zip', string='Destination Zip', readonly=True)
    destination_city = fields.Char(related='request_id.destination_city', string='Destination City', readonly=True)
    destination_state_id = fields.Many2one(related='request_id.destination_state_id', string='Destination State', readonly=True)
    destination_country_id = fields.Many2one(related='request_id.destination_country_id', string='Destination Country', readonly=True)
    cargo_summary = fields.Text(string='Cargo')
    weight_kg = fields.Float(string='Weight (kg)')
    volume_m3 = fields.Float(string='Volume (m3)')
    pickup_date = fields.Datetime(string='Pickup Date')
    delivery_deadline = fields.Datetime(string='Delivery Deadline')
    line_ids = fields.One2many('tlmp.transport.inquiry.line', 'inquiry_id',
                               string='Inquiry Lines')
    quote_ids = fields.One2many('tlmp.transport.quote', 'inquiry_id',
                                string='Customer Quotes')
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
        self.ensure_one()
        if self.state != 'responded':
            raise UserError(_('Only responded carrier inquiries can be selected.'))
        self.write({'state': 'accepted'})
        return True

    def action_create_quote(self):
        self.ensure_one()
        if self.state != 'accepted':
            raise UserError(_('Select a carrier first (Inquiry state = Accepted/Selected).'))
        existing = self.env['tlmp.transport.quote'].search(
            [('inquiry_id', '=', self.id)], limit=1)
        if existing:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'tlmp.transport.quote',
                'view_mode': 'form',
                'res_id': existing.id,
                'target': 'current',
            }
        charge_item = self.env['world.depot.charge.item'].search(
            [('item_name', '=', 'Transportation Fee')], limit=1) or \
            self.env['world.depot.charge.item'].search([], limit=1)
        quote = self.env['tlmp.transport.quote'].create({
            'request_id': self.request_id.id if self.request_id else False,
            'inquiry_id': self.id,
            'partner_id': self.request_id.partner_id.id if self.request_id and self.request_id.partner_id else False,
            'carrier_cost': self.total_amount,
            'line_ids': [(0, 0, {
                'description': ' - '.join(
                    x for x in (cl.description, cl.container_no, cl.bl_number) if x) or _('Cargo'),
                'quantity': 1.0,
                'unit_price': 0.0,
            }) for cl in self.request_id.cargo_line_ids] if self.request_id else [],
            'fee_line_ids': [(0, 0, {
                'fee_type_id': charge_item.id if charge_item else False,
                'party_type': 'customer_charge',
                'source_type': 'commercial',
                'unit_amount': self.total_amount,
                'quantity': 1.0,
                'description': 'Transportation Fee',
            })] if charge_item else [],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tlmp.transport.quote',
            'view_mode': 'form',
            'res_id': quote.id,
            'target': 'current',
        }

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
