"""Evaluator — parses condition_expression catalog into true/false.
Supports AND/OR/NOT + gt/lt/eq/contains/is_null.
Field names must come from field_catalog whitelist."""
import json
from odoo import api, models, _
from odoo.exceptions import ValidationError

ALLOWED_OPS = {'gt', 'lt', 'eq', 'contains', 'is_null'}
ALLOWED_BOOL = {'AND', 'OR', 'NOT'}


class RuleEvaluator(models.AbstractModel):
    _name = 'tlmp.rule.evaluator'
    _description = 'Rule Condition Evaluator'

    @api.model
    def evaluate(self, condition_expression, context_data):
        """Evaluate condition_expression JSON against context_data dict.
        context_data: {field_name: value} — must match field_catalog.
        Returns True/False."""
        if isinstance(condition_expression, str):
            try:
                condition_expression = json.loads(condition_expression)
            except (json.JSONDecodeError, TypeError):
                raise ValidationError(_('Invalid condition_expression JSON'))
        if not isinstance(condition_expression, dict):
            raise ValidationError(_('condition_expression must be a dict'))

        return self._evaluate_node(condition_expression, context_data)

    def _evaluate_node(self, node, ctx):
        if 'operator' in node:
            return self._evaluate_compare(node, ctx)
        for bool_op in ALLOWED_BOOL:
            if bool_op in node:
                return self._evaluate_bool(bool_op, node[bool_op], ctx)
        if 'field' in node:
            return self._evaluate_compare(node, ctx)
        raise ValidationError(_('Unknown condition_expression node: %s') % list(node.keys()))

    def _evaluate_compare(self, node, ctx):
        op = node.get('operator')
        field = node.get('field')
        if op not in ALLOWED_OPS:
            raise ValidationError(_('Operator %s not allowed. Use: %s') % (op, ALLOWED_OPS))
        actual = ctx.get(field)
        expected = node.get('value')
        if op == 'gt':
            return float(actual or 0) > float(expected or 0)
        elif op == 'lt':
            return float(actual or 0) < float(expected or 0)
        elif op == 'eq':
            return str(actual) == str(expected)
        elif op == 'contains':
            return str(expected or '') in str(actual or '')
        elif op == 'is_null':
            return actual is None or actual == '' or actual == False
        return False

    def _evaluate_bool(self, bool_op, nodes, ctx):
        if bool_op == 'AND':
            return all(self._evaluate_node(n, ctx) for n in nodes)
        elif bool_op == 'OR':
            return any(self._evaluate_node(n, ctx) for n in nodes)
        elif bool_op == 'NOT':
            return not self._evaluate_node(nodes[0], ctx) if nodes else True
        return False
