# -*- coding: utf-8 -*-
"""Sprint38: Exception Rule Engine tests."""
import json
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestExceptionRule(TransactionCase):
    """Rule CRUD + lifecycle + version control."""

    def setUp(self):
        super().setUp()
        self.rule = self.env['tlmp.settlement.exception.rule'].create({
            'code': 'TEST_MATCH_FAILED',
            'name': 'Test Match Failed Rule',
            'exception_type': 'MATCH_FAILED',
            'condition_expression': json.dumps({
                'operator': 'lt', 'field': 'matching_confidence', 'value': 0.7
            }),
            'rule_state': 'draft',
            'version': '1.0',
        })

    def test_01_rule_create(self):
        self.assertTrue(self.rule.id)
        self.assertEqual(self.rule.rule_state, 'draft')

    def test_02_rule_activate(self):
        self.rule.action_activate()
        self.assertEqual(self.rule.rule_state, 'active')

    def test_03_single_active_version(self):
        self.rule.action_activate()
        v2 = self.env['tlmp.settlement.exception.rule'].create({
            'code': 'TEST_MATCH_FAILED',
            'name': 'Test V2',
            'exception_type': 'MATCH_FAILED',
            'condition_expression': '{}',
            'version': '2.0',
        })
        v2.action_activate()
        self.assertEqual(v2.rule_state, 'active')
        self.assertEqual(self.rule.rule_state, 'deprecated')

    def test_04_code_version_unique(self):
        with self.assertRaises(Exception):
            self.env['tlmp.settlement.exception.rule'].create({
                'code': 'TEST_MATCH_FAILED',
                'name': 'Duplicate',
                'exception_type': 'MATCH_FAILED',
                'condition_expression': '{}',
                'version': '1.0',
            })


class TestRuleEvaluator(TransactionCase):

    def setUp(self):
        super().setUp()
        self.evaluator = self.env['tlmp.rule.evaluator']

    def test_01_gt(self):
        expr = {'operator': 'gt', 'field': 'billing_amount', 'value': 100}
        self.assertTrue(self.evaluator.evaluate(expr, {'billing_amount': 200}))
        self.assertFalse(self.evaluator.evaluate(expr, {'billing_amount': 50}))

    def test_02_lt(self):
        expr = {'operator': 'lt', 'field': 'matching_confidence', 'value': 0.7}
        self.assertTrue(self.evaluator.evaluate(expr, {'matching_confidence': 0.5}))
        self.assertFalse(self.evaluator.evaluate(expr, {'matching_confidence': 0.9}))

    def test_03_eq(self):
        expr = {'operator': 'eq', 'field': 'carrier_code', 'value': 'DHL'}
        self.assertTrue(self.evaluator.evaluate(expr, {'carrier_code': 'DHL'}))
        self.assertFalse(self.evaluator.evaluate(expr, {'carrier_code': 'UPS'}))

    def test_04_and(self):
        expr = {'AND': [
            {'operator': 'gt', 'field': 'billing_amount', 'value': 100},
            {'operator': 'eq', 'field': 'carrier_code', 'value': 'DHL'},
        ]}
        self.assertTrue(self.evaluator.evaluate(expr, {'billing_amount': 200, 'carrier_code': 'DHL'}))
        self.assertFalse(self.evaluator.evaluate(expr, {'billing_amount': 50, 'carrier_code': 'DHL'}))

    def test_05_or(self):
        expr = {'OR': [
            {'operator': 'lt', 'field': 'matching_confidence', 'value': 0.5},
            {'operator': 'gt', 'field': 'billing_amount', 'value': 1000},
        ]}
        self.assertTrue(self.evaluator.evaluate(expr, {'matching_confidence': 0.3}))
        self.assertFalse(self.evaluator.evaluate(expr, {'matching_confidence': 0.9, 'billing_amount': 500}))

    def test_06_not(self):
        expr = {'NOT': [{'operator': 'eq', 'field': 'carrier_code', 'value': 'DHL'}]}
        self.assertTrue(self.evaluator.evaluate(expr, {'carrier_code': 'UPS'}))
        self.assertFalse(self.evaluator.evaluate(expr, {'carrier_code': 'DHL'}))

    def test_07_forbidden_operator(self):
        with self.assertRaises(ValidationError):
            self.evaluator.evaluate({'operator': 'eval', 'field': 'x', 'value': '1+1'}, {})


class TestRuleActionExecutor(TransactionCase):
    """Action idempotency + duplicate prevention."""

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test', 'is_company': True})
        self.rule = self.env['tlmp.settlement.exception.rule'].create({
            'code': 'ACT_TEST',
            'name': 'Action Test',
            'exception_type': 'MATCH_FAILED',
            'condition_expression': '{}',
            'rule_state': 'active',
        })
        self.executor = self.env['tlmp.rule.action.executor']

    def test_01_create_exception(self):
        ctx = {'source_model': 'res.partner', 'source_res_id': self.partner.id,
               'source_display_name': self.partner.name, 'snapshot': {}}
        result = self.executor.execute(self.rule, ctx)
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result.get('exception_id'))

    def test_02_idempotency(self):
        ctx = {'source_model': 'res.partner', 'source_res_id': self.partner.id,
               'source_display_name': self.partner.name, 'snapshot': {}}
        r1 = self.executor.execute(self.rule, ctx)
        r2 = self.executor.execute(self.rule, ctx)
        self.assertEqual(r2['status'], 'skipped')
        self.assertEqual(r2.get('reason'), 'already_executed')

    def test_03_duplicate_prevention(self):
        ctx = {'source_model': 'res.partner', 'source_res_id': self.partner.id,
               'source_display_name': self.partner.name, 'snapshot': {}}
        r1 = self.executor.execute(self.rule, ctx)
        exc = self.env['tlmp.settlement.exception'].browse(r1['exception_id'])
        self.assertEqual(exc.creation_method, 'rule_engine')
        self.assertTrue(exc.rule_execution_id)


class TestRuleScope(TransactionCase):
    """Scope isolation tests."""

    def test_01_scope_global(self):
        rule = self.env['tlmp.settlement.exception.rule'].create({
            'code': 'SCOPE_GLOBAL', 'name': 'Global', 'exception_type': 'MATCH_FAILED',
            'condition_expression': '{}', 'scope_type': 'global',
        })
        self.assertEqual(rule.scope_type, 'global')

    def test_02_scope_carrier(self):
        partner = self.env['res.partner'].create({'name': 'DHL', 'is_company': True})
        rule = self.env['tlmp.settlement.exception.rule'].create({
            'code': 'SCOPE_DHL', 'name': 'DHL Rule', 'exception_type': 'MATCH_FAILED',
            'condition_expression': '{}', 'scope_type': 'carrier',
            'carrier_partner_id': partner.id,
        })
        self.assertEqual(rule.carrier_partner_id.id, partner.id)
