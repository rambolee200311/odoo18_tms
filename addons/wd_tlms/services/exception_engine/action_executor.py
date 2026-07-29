"""Action Executor — executes rule actions with idempotency and safety checks.
Only allows exception domain actions (CREATE_EXCEPTION, SET_PRIORITY, AUTO_CLOSE_EXCEPTION, CREATE_CASE).
Forbidden: UPDATE_BUSINESS_DATA, MODIFY_ALLOCATION, MODIFY_BILLING."""
import json, hashlib
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RuleActionExecutor(models.AbstractModel):
    _name = 'tlmp.rule.action.executor'
    _description = 'Rule Action Executor'

    @api.model
    def execute(self, rule, context_data):
        """Execute rule action with idempotency check."""
        execution_id = self._compute_execution_id(rule, context_data)
        existing = self.env['tlmp.settlement.exception.rule.execution'].search([
            ('execution_id', '=', execution_id)], limit=1)
        if existing:
            return {'status': 'skipped', 'reason': 'already_executed', 'execution_id': execution_id}

        action = rule.action_type
        result = {'execution_id': execution_id, 'action': action}

        if action == 'create_exception':
            exc = self._create_exception(rule, context_data)
            result['exception_id'] = exc.id
        elif action == 'set_priority':
            exc = self._find_exception(context_data)
            if exc:
                exc.write({'priority': rule.exception_priority})
                result['exception_id'] = exc.id
        elif action == 'auto_close_exception':
            exc = self._find_or_create_exception(rule, context_data)
            if exc and exc.state not in ('closed', 'cancelled'):
                exc.resolution_note = 'Auto-closed by rule: %s' % rule.name
                exc.action_auto_resolve() if hasattr(exc, 'action_auto_resolve') else None
                result['exception_id'] = exc.id

        self._record_execution(execution_id, rule, context_data, result)
        return {'status': 'ok', **result}

    def _compute_execution_id(self, rule, ctx):
        raw = '%s|%s|%s|%s' % (rule.id, ctx.get('source_model', ''),
                                ctx.get('source_res_id', ''), str(datetime.now().hour))
        return hashlib.md5(raw.encode()).hexdigest()[:20]

    def _check_active_exception(self, rule, ctx):
        existing = self.env['tlmp.settlement.exception'].search([
            ('exception_type', '=', rule.exception_type),
            ('source_model', '=', ctx.get('source_model', '')),
            ('source_res_id', '=', ctx.get('source_res_id', 0)),
            ('state', 'not in', ('closed', 'cancelled')),
        ], limit=1)
        return existing

    def _create_exception(self, rule, ctx):
        existing = self._check_active_exception(rule, ctx)
        if existing:
            return existing
        return self.env['tlmp.settlement.exception'].create({
            'exception_type': rule.exception_type,
            'priority': rule.exception_priority,
            'description': ctx.get('description', 'Rule: %s' % rule.name),
            'source_model': ctx.get('source_model', ''),
            'source_res_id': ctx.get('source_res_id', 0),
            'source_display_name': ctx.get('source_display_name', ''),
            'source_snapshot': json.dumps(ctx.get('snapshot', {}), default=str),
            'source_captured_at': fields.Datetime.now(),
            'creation_method': 'rule_engine',
        })

    def _record_execution(self, execution_id, rule, ctx, result):
        exception_id = result.get('exception_id')
        self.env['tlmp.settlement.exception.rule.execution'].create({
            'rule_id': rule.id,
            'execution_id': execution_id,
            'matched': True,
            'source_model': ctx.get('source_model', ''),
            'source_res_id': ctx.get('source_res_id', 0),
            'created_exception_id': exception_id,
        })
        if exception_id:
            self.env['tlmp.settlement.exception'].browse(exception_id).write({
                'rule_execution_id': self.env['tlmp.settlement.exception.rule.execution'].search(
                    [('execution_id', '=', execution_id)], limit=1).id,
            })
