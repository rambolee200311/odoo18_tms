# -*- coding: utf-8 -*-
"""Sprint44/45: scene-driven address architecture tests"""
from odoo.tests.common import TransactionCase


class TestSceneAddress(TransactionCase):
    def setUp(self):
        super().setUp()
        self.wh1 = self.env['stock.warehouse'].create({'name': 'WH1', 'code': 'WH1'})
        self.terminal = self.env['res.partner'].create({
            'name': 'Rotterdam Terminal',
            'street': 'Boompijes 258',
            'zip': '3011XZ',
            'city': 'Rotterdam',
        })
        self.customer = self.env['res.partner'].create({
            'name': 'Test Customer',
            'street': 'Main St 1',
            'city': 'Amsterdam',
        })
        self.scene_tw = self.env['tlmp.transport.scene'].search(
            [('code', '=', 'terminal_to_warehouse')], limit=1)
        self.scene_tc = self.env['tlmp.transport.scene'].search(
            [('code', '=', 'terminal_to_customer')], limit=1)

    def _mk_request(self, scene=None, **kw):
        vals = {
            'request_type': 'plan_driven',
            'destination_type': 'warehouse',
            'cargo_type': 'container',
            'scene_id': (scene or self.scene_tw).id,
            'terminal_id': self.terminal.id,
            'warehouse_id': self.wh1.id,
            'origin_street': self.terminal.street,
            'origin_zip': self.terminal.zip,
            'origin_city': self.terminal.city,
            'destination_street': 'Warehouse St 1',
            'destination_city': 'Rotterdam',
        }
        vals.update(kw)
        return self.env['tlmp.transport.request'].create(vals)

    def test_pickup_plan_address_snapshot(self):
        """action_go_schedule creates plan and copies address from request"""
        req = self._mk_request()
        req.action_go_schedule()
        plan = self.env['pickup.plan'].search(
            [('transport_request_id', '=', req.id)], limit=1)
        self.assertTrue(plan, 'Pickup Plan should be created')
        self.assertEqual(plan.origin_street, self.terminal.street)
        self.assertEqual(plan.origin_city, self.terminal.city)
        self.assertEqual(plan.destination_city, 'Rotterdam')

    def test_inquiry_address_related(self):
        """Inquiry projects address from request via related fields"""
        req = self._mk_request(scene=self.scene_tc, destination_type='customer',
                               partner_id=self.customer.id)
        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': req.id,
            'partner_id': self.customer.id,
        })
        self.assertEqual(inquiry.origin_street, self.terminal.street)
        self.assertEqual(inquiry.destination_street, 'Warehouse St 1')

    def test_manual_override_not_overwritten(self):
        """User-edited address is not overwritten by auto-fill"""
        req = self._mk_request(origin_street='User Edited Street')
        req._onchange_terminal_id()
        self.assertEqual(req.origin_street, 'User Edited Street')
        self.assertEqual(req.origin_city, self.terminal.city)
