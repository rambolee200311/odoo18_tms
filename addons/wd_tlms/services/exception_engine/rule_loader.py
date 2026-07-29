"""Rule Loader — DB to runtime cache. Sprint39: support multi-worker cache invalidation."""
import json
from odoo import api, models


class RuleLoader(models.AbstractModel):
    _name = 'tlmp.rule.loader'
    _description = 'Exception Rule Loader'

    @api.model
    def load_active_rules(self):
        """Load all active rules ordered by rule_sequence."""
        return self.env['tlmp.settlement.exception.rule'].search([
            ('rule_state', '=', 'active'),
        ], order='rule_sequence, code')

    @api.model
    def load_rules_for_scope(self, scope_type='global', carrier_id=False, customer_id=False, scene_id=False):
        """Load rules matching a specific scope. GLOBAL rules always included."""
        domain = ['|', ('scope_type', '=', 'global'), ('scope_type', '=', scope_type)]
        if scope_type == 'carrier' and carrier_id:
            domain = ['|', ('scope_type', '=', 'global'),
                      '&', ('scope_type', '=', 'carrier'), ('carrier_partner_id', '=', carrier_id)]
        return self.env['tlmp.settlement.exception.rule'].search(
            domain + [('rule_state', '=', 'active')],
            order='rule_sequence, code')
