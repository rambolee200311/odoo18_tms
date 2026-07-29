from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json

class SettlementExceptionRule(models.Model):
    _name = 'tlmp.settlement.exception.rule'
    _description = 'Settlement Exception Rule'
    _rec_name = 'name'
    _order = 'code, version desc'

    code = fields.Char(string='Rule Code', required=True, index=True)
    name = fields.Char(string='Rule Name', required=True)
    exception_type = fields.Selection([
        ('MATCH_FAILED', 'Match Failed'),
        ('AMOUNT_MISMATCH', 'Amount Mismatch'),
        ('DUPLICATE_INVOICE', 'Duplicate Invoice'),
        ('INVALID_REFERENCE', 'Invalid Reference'),
        ('IMPORT_ERROR', 'Import Error'),
        ('APPROVAL_TIMEOUT', 'Approval Timeout'),
    ], string='Exception Type', required=True)
    condition_expression = fields.Text(string='Condition (JSON)', required=True)
    rule_sequence = fields.Integer(string='Rule Sequence', default=10)
    exception_priority = fields.Selection([
        ('urgent', 'Urgent'), ('high', 'High'),
        ('normal', 'Normal'), ('low', 'Low'),
    ], string='Exception Priority', default='normal')
    action_type = fields.Selection([
        ('create_exception', 'Create Exception'),
        ('set_priority', 'Set Priority'),
        ('auto_close_exception', 'Auto Close Exception'),
        ('create_case', 'Create Case'),
    ], string='Action Type', default='create_exception')
    rule_state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
    ], string='Rule State', default='draft', required=True)
    version = fields.Char(string='Version', required=True, default='1.0')
    effective_from = fields.Date(string='Effective From')
    effective_to = fields.Date(string='Effective To')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.uid)
    approved_by = fields.Many2one('res.users', string='Approved By')
    published_at = fields.Datetime(string='Published At')
    scope_type = fields.Selection([
        ('global', 'Global'),
        ('carrier', 'Carrier'),
        ('customer', 'Customer'),
        ('scene', 'Scene'),
    ], string='Scope Type', default='global', required=True)
    carrier_partner_id = fields.Many2one('res.partner', string='Carrier')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    _sql_constraints = [
        ('code_version_unique', 'unique(code, version)', 'Rule code + version must be unique.'),
    ]
    def action_activate(self):
        for r in self:
            old = self.search([('code','=',r.code),('rule_state','=','active'),('id','!=',r.id)])
            old.write({'rule_state':'deprecated','effective_to':fields.Date.today()})
        self.write({'rule_state':'active','published_at':fields.Datetime.now()})
    def action_deprecate(self):
        self.write({'rule_state':'deprecated','effective_to':fields.Date.today()})
    def action_draft(self):
        self.write({'rule_state':'draft'})
