# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreateCarrierInquiryWizard(models.TransientModel):
    """Create a carrier inquiry and record its response in one step."""

    _name = 'tlmp.create.carrier.inquiry.wizard'
    _description = 'Create Carrier Inquiry'

    request_id = fields.Many2one(
        'tlmp.transport.request', string='Request', required=True,
        default=lambda self: self.env.context.get('active_id'))
    carrier_id = fields.Many2one(
        'res.partner', string='Carrier', required=True,
        domain=[('is_carrier', '=', True)])
    unit_price = fields.Monetary(string='Unit Price', default=0.0)
    quantity = fields.Float(string='Quantity', default=1.0)
    carrier_cost = fields.Monetary(
        string='Carrier Cost', compute='_compute_carrier_cost')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)
    response_date = fields.Datetime(
        string='Response Date', default=fields.Datetime.now)
    validity_date = fields.Date(string='Valid Until')
    carrier_notes = fields.Text(string='Carrier Notes')

    @api.depends('unit_price', 'quantity')
    def _compute_carrier_cost(self):
        for wizard in self:
            wizard.carrier_cost = (
                (wizard.unit_price or 0.0) * (wizard.quantity or 0.0))

    @api.onchange('request_id')
    def _onchange_request_id(self):
        if self.request_id and not self.carrier_id:
            self.carrier_id = self.request_id.carrier_id.id or False

    def action_create(self):
        self.ensure_one()
        request = self.request_id
        if request.request_type != 'commercial':
            raise UserError(
                _('Carrier inquiries require a commercial request.'))
        if request.has_accepted_quote:
            raise UserError(_('This request already has an accepted quote.'))
        if not self.carrier_cost:
            raise UserError(_('Carrier cost must be greater than zero.'))

        cargo_summary = request.cargo_description
        cargo_lines = request.cargo_line_ids
        if not cargo_summary and cargo_lines:
            cargo_summary = '\n'.join(
                ' - '.join(x for x in (
                    cl.description, cl.container_no, cl.bl_number) if x)
                for cl in cargo_lines)
        if not cargo_summary and request.cargo_type == 'pallet':
            cargo_summary = _('Pallet %s / Package %s') % (
                request.pallet_count or 0, request.package_count or 0)
        if not cargo_summary and request.cargo_type == 'piece':
            cargo_summary = _('Pieces %s') % (request.package_count or 0)

        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': request.id,
            'partner_id': self.carrier_id.id,
            'cargo_summary': cargo_summary or '',
            'weight_kg': request.cargo_weight or sum(
                cl.gross_weight for cl in cargo_lines),
            'volume_m3': request.cargo_volume or sum(
                cl.volume_m3 for cl in cargo_lines),
            'pickup_date': request.requested_pickup_date,
            'validity_date': self.validity_date,
            'carrier_notes': self.carrier_notes,
            'line_ids': [(0, 0, {
                'description': cargo_summary or _('Cargo'),
                'unit_price': self.unit_price or 0.0,
                'quantity': self.quantity or 1.0,
            })],
        })
        inquiry.action_send()
        inquiry.action_respond(response_date=self.response_date)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tlmp.transport.request',
            'view_mode': 'form',
            'res_id': request.id,
            'target': 'current',
        }
