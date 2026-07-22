from odoo import models, fields, api, _


class FeeLine(models.Model):
    _name = 'transport.fee.line'
    _description = 'Fee Line'
    _order = 'id'

    fee_type_id = fields.Many2one(
        'transport.fee.type', string='Fee Type', required=True)
    rate_base_id = fields.Many2one(
        'transport.rate.base', string='Rate Base',
        help='Optional reference to the rate used to calculate this fee.')

    source_type = fields.Selection([
        ('commercial', 'Commercial'),
        ('plan_driven', 'Plan-Driven'),
    ], string='Source Type', required=True,
        help='Identifies which business flow this fee belongs to.')
    source_quote_id = fields.Many2one(
        'tlmp.transport.quote', string='Source Quote',
        index=True, ondelete='cascade',
        help='Quote this fee belongs to (commercial flow).')
    source_order_id = fields.Many2one(
        'tlmp.transport.order', string='Source Order',
        index=True, ondelete='cascade',
        help='Order this fee belongs to (plan-driven or final order).')

    quantity = fields.Float(string='Quantity', default=1.0)
    unit_amount = fields.Monetary(string='Unit Amount', default=0.0)
    total_amount = fields.Monetary(
        string='Total Amount',
        compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)

    description = fields.Text(string='Description')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    @api.depends('quantity', 'unit_amount')
    def _compute_total_amount(self):
        for r in self:
            r.total_amount = (r.quantity or 0.0) * (r.unit_amount or 0.0)
