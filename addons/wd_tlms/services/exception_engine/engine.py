"""Rule Engine — main orchestrator. Rule priority → Legacy Handler fallback."""
import json
from odoo import api, models, _


class RuleEngine(models.AbstractModel):
    _name = 'tlmp.rule.engine'
    _description = 'Settlement Exception Rule Engine'

    @api.model
    def scan(self, source_model, source_id, context_data=None):
        """Scan rules for a source record. Rule Engine priority → Handler fallback."""
        ctx = context_data or {}
        rules = self.env['tlmp.rule.loader'].load_active_rules()
        for rule in rules:
            try:
                matched = self.env['tlmp.rule.evaluator'].evaluate(
                    rule.condition_expression, ctx)
            except Exception:
                continue
            if matched:
                return self.env['tlmp.rule.action.executor'].execute(rule, ctx)
        return self._fallback_handler(source_model, source_id, ctx)

    def _fallback_handler(self, source_model, source_id, ctx):
        handler = self.env.get('tlmp.exception.handler.legacy')
        if handler:
            return handler.handle(source_model, source_id, ctx)
        return {'status': 'skipped', 'reason': 'no_rule_match_no_handler'}
