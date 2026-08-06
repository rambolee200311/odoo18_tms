# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TransportEventLedger(models.Model):
    """Generic five-model event ledger for TLMS Workflow Engine."""

    _name = 'tlmp.transport.event.ledger'
    _description = 'Transport Event Ledger'
    _order = 'create_date desc, id desc'
    _rec_name = 'display_name'

    res_model = fields.Char(string='Document Model', required=True, index=True)
    res_id = fields.Integer(string='Document ID', required=True, index=True)
    event_type = fields.Char(string='Event Code', required=True, index=True)
    event_category = fields.Selection([
        ('business', 'Business'),
        ('state', 'State'),
        ('integration', 'Integration'),
    ], string='Event Category', required=True, default='state')
    from_state = fields.Char(string='From State')
    to_state = fields.Char(string='To State')
    payload = fields.Text(string='Payload')
    create_uid = fields.Many2one(
        'res.users', string='Operator', readonly=True,
        default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Recorded At', readonly=True)
    display_name = fields.Char(
        string='Display Name', compute='_compute_display_name')

    @api.depends('event_type', 'res_model', 'res_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = '%s [%s#%s]' % (
                r.event_type, r.res_model, r.res_id)
