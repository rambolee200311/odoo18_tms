# -*- coding: utf-8 -*-
"""Sprint39: Settlement Domain schema upgrade test — Sprint30→39.
Verifies existing models/fields are correctly defined."""
from odoo.tests.common import TransactionCase


class TestSettlementUpgrade(TransactionCase):

    def test_01_billing_document_exists(self):
        model = self.env['ir.model'].search([('model', '=', 'tlmp.carrier.billing.document')])
        self.assertTrue(model)

    def test_02_billing_line_exists(self):
        model = self.env['ir.model'].search([('model', '=', 'tlmp.carrier.billing.line')])
        self.assertTrue(model)

    def test_03_allocation_exists(self):
        self.assertTrue(self.env['ir.model'].search([('model', '=', 'tlmp.carrier.settlement.allocation')]))

    def test_04_batch_exists(self):
        self.assertTrue(self.env['ir.model'].search([('model', '=', 'tlmp.carrier.settlement.batch')]))

    def test_05_case_exists(self):
        self.assertTrue(self.env['ir.model'].search([('model', '=', 'tlmp.carrier.settlement.case')]))

    def test_06_exception_exists(self):
        self.assertTrue(self.env['ir.model'].search([('model', '=', 'tlmp.settlement.exception')]))

    def test_07_rule_exists(self):
        self.assertTrue(self.env['ir.model'].search([('model', '=', 'tlmp.settlement.exception.rule')]))

    def test_08_rule_execution_exists(self):
        self.assertTrue(self.env['ir.model'].search([('model', '=', 'tlmp.settlement.exception.rule.execution')]))

    def test_09_exception_has_creation_method(self):
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'tlmp.settlement.exception'),
            ('name', '=', 'creation_method'),
        ])
        self.assertTrue(field)

    def test_10_rule_has_condition_expression(self):
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'tlmp.settlement.exception.rule'),
            ('name', '=', 'condition_expression'),
        ])
        self.assertTrue(field)
