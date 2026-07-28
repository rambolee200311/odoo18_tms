from odoo import api, fields, models, _


class CarrierInvoiceTemplate(models.Model):
    """承运商账单导入模板 — 可配置映射，新增承运商无需开发"""
    _name = 'tlmp.carrier.invoice.template'
    _description = 'Carrier Invoice Template'
    _rec_name = 'name'

    name = fields.Char(string='Template Name', required=True)
    carrier_profile_id = fields.Many2one(
        'tlmp.carrier.profile', string='Carrier Profile', required=True)
    file_type = fields.Selection([
        ('csv', 'CSV'),
        ('xlsx', 'Excel (.xlsx)'),
    ], string='File Type', required=True, default='csv')
    mapping_json = fields.Text(
        string='Mapping Config (JSON)',
        required=True,
        help='格式: {"column_key":"business_field"}，不绑定业务字段名')
    encoding = fields.Selection([
        ('utf-8', 'UTF-8'),
        ('gbk', 'GBK'),
        ('iso-8859-1', 'ISO-8859-1'),
        ('auto', 'Auto Detect'),
    ], string='Encoding', default='auto')
    delimiter = fields.Char(string='CSV Delimiter', default=',')
    has_header = fields.Boolean(string='Has Header Row', default=True)
    is_active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_carrier_unique',
         'unique(name, carrier_profile_id, company_id)',
         'Template name must be unique per carrier.'),
    ]
