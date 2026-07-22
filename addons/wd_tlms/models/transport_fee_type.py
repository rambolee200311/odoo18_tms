from odoo import models, fields, api, _


class FeeType(models.Model):
    _name = 'transport.fee.type'
    _description = 'Fee Type'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(string='Fee Name', required=True, index=True)
    code = fields.Char(string='Fee Code', required=True, index=True)
    category = fields.Selection([
        ('transport', 'Transport'),
        ('handling', 'Handling'),
        ('storage', 'Storage'),
        ('customs', 'Customs'),
        ('other', 'Other'),
    ], string='Category', default='transport', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_fee_code', 'UNIQUE(code)', _('Fee Code must be unique.')),
    ]
