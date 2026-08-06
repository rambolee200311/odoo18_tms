"""Sprint50: Workflow Engine, Event Ledger and 49-B integration tests."""

import json

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestWorkflowEngine(TransactionCase):
    """Foundation: ledger-before-state transitions and 49-B snapshot wiring."""

    def setUp(self):
        super().setUp()
        self.scene = self.env['tlmp.transport.scene'].search(
            [('code', '=', 'terminal_to_warehouse')], limit=1
        ) or self.env['tlmp.transport.scene'].create({
            'name': 'Test S1', 'code': 'terminal_to_warehouse',
            'scene_type': 'plan_driven', 'destination_type': 'warehouse',
        })
        self.wh = self.env['stock.warehouse'].search([], limit=1)
        self.transport_type = self.env['tlmp.transport.type'].search(
            [], limit=1)

    def _request(self, **kwargs):
        vals = {
            'scene_id': self.scene.id,
            'request_type': 'plan_driven',
            'cargo_type': kwargs.get('cargo_type', 'container'),
            'carrier_type': kwargs.get('carrier_type', 'truck'),
            'vehicle_body_type': kwargs.get('vehicle_body_type', 'no_requirement'),
            'vehicle_capacity_requirement': kwargs.get(
                'vehicle_capacity_requirement', 'no_limit'),
            'dg_attribute': kwargs.get('dg_attribute', 'normal'),
            'has_dangerous_goods': kwargs.get('has_dangerous_goods', False),
            'warehouse_id': self.wh.id,
            'requested_qty': kwargs.get('requested_qty', 100.0),
        }
        return self.env['tlmp.transport.request'].create(vals)

    def _order(self, req, **kwargs):
        return self.env['tlmp.transport.order'].create({
            'request_id': req.id,
            'transport_type_id': self.transport_type.id,
            'state': kwargs.get('state', 'draft'),
            'cargo_weight': kwargs.get('cargo_weight', 100.0),
            'delivered_qty': kwargs.get('delivered_qty', 0.0),
        })

    def _ledger(self, req, event_type):
        return self.env['tlmp.transport.event.ledger'].search([
            ('res_model', '=', 'tlmp.transport.request'),
            ('res_id', '=', req.id),
            ('event_type', '=', event_type),
        ], limit=1)

    # -----------------------------------------------------------
    # Request: submit -> process -> complete + ledger
    # -----------------------------------------------------------
    def test_01_request_submit_writes_ledger_and_validation(self):
        req = self._request()
        req.action_submit()
        self.assertEqual(req.state, 'submitted')
        self.assertEqual(req.validation_state, 'passed')
        self.assertEqual(req.matrix_snapshot_status, 'frozen')
        self.assertTrue(req.vehicle_requirement_mode_snapshot)
        self.assertTrue(self._ledger(req, 'REQUEST_SUBMITTED'))

    def test_02_processing_guard(self):
        req = self._request()
        req.action_submit()
        req.action_process()
        self.assertEqual(req.state, 'processing')
        self.assertTrue(self._ledger(req, 'REQUEST_PROCESSING'))
        draft = self._request()
        with self.assertRaises(UserError):
            draft.action_process()

    def test_03_complete_requires_closed_orders(self):
        req = self._request()
        req.action_submit()
        req.action_process()
        order = self._order(req, state='draft')
        with self.assertRaises(UserError):
            req.action_complete()
        order.write({'state': 'settled', 'delivered_qty': 100.0})
        req.invalidate_recordset()
        req.action_complete()
        self.assertEqual(req.state, 'completed')
        self.assertEqual(req.fulfillment_status, 'completed')
        self.assertTrue(self._ledger(req, 'REQUEST_COMPLETED'))

    def test_04_legacy_confirm_writes_ledger(self):
        req = self._request()
        req.action_confirm()
        self.assertEqual(req.state, 'confirmed')
        self.assertEqual(req.validation_state, 'passed')
        self.assertTrue(self._ledger(req, 'REQUEST_CONFIRMED'))

    def test_05_cancel_writes_ledger(self):
        req = self._request()
        req.action_submit()
        req.action_cancel()
        self.assertEqual(req.state, 'cancelled')
        self.assertTrue(self._ledger(req, 'REQUEST_CANCELLED'))

    # -----------------------------------------------------------
    # Order: allocate / exception / settlement
    # -----------------------------------------------------------
    def test_06_order_allocate_snapshot(self):
        req = self._request(
            vehicle_body_type='reefer_refrigerated',
            vehicle_capacity_requirement='below_40t')
        req.action_confirm()
        order = self._order(req, state='confirmed')
        order.action_allocate()
        self.assertEqual(order.state, 'allocated')
        snapshot = json.loads(order.vehicle_allocation_snapshot)
        self.assertEqual(
            snapshot['vehicle_requirement_mode'], 'required')
        self.assertEqual(
            snapshot['vehicle_body_type'], 'reefer_refrigerated')
        self.assertTrue(self.env['tlmp.transport.event.ledger'].search([
            ('res_model', '=', 'tlmp.transport.order'),
            ('res_id', '=', order.id),
            ('event_type', '=', 'ORDER_ALLOCATED'),
        ], limit=1))

    def test_07_order_exception_recovery(self):
        req = self._request()
        req.action_confirm()
        order = self._order(req, state='confirmed')
        order.action_allocate()
        order.action_raise_exception(
            exception_type='delay', recovery='in_transit')
        self.assertEqual(order.state, 'exception')
        self.assertEqual(order.exception_type, 'delay')
        order.action_recover_exception()
        self.assertEqual(order.state, 'in_transit')

    # -----------------------------------------------------------
    # Quote / Inquiry / Plan
    # -----------------------------------------------------------
    def test_08_quote_confirmation_flow(self):
        req = self._request()
        quote = self.env['tlmp.transport.quote'].create({
            'request_id': req.id,
            'carrier_cost': 100.0,
        })
        quote.action_issue()
        self.assertEqual(quote.state, 'issued')
        quote.action_approve()
        self.assertEqual(quote.state, 'approved')
        quote.customer_accept = True
        quote.action_confirm_customer()
        self.assertEqual(quote.state, 'confirmed')
        self.assertEqual(quote.confirmation_source, 'customer')
        self.assertTrue(self.env['tlmp.transport.event.ledger'].search([
            ('res_model', '=', 'tlmp.transport.quote'),
            ('res_id', '=', quote.id),
            ('event_type', '=', 'QUOTE_CONFIRMED'),
        ], limit=1))

    def test_09_inquiry_close(self):
        req = self._request()
        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': req.id,
            'cargo_summary': 'Test cargo',
        })
        inquiry.action_send()
        inquiry.action_close(
            reason='carrier_selected', carrier_id=self.env.ref(
                'base.partner_root').id)
        self.assertEqual(inquiry.state, 'closed')
        self.assertEqual(inquiry.close_reason, 'carrier_selected')
        self.assertTrue(inquiry.selected_carrier_id)
        self.assertTrue(self.env['tlmp.transport.event.ledger'].search([
            ('res_model', '=', 'tlmp.transport.inquiry'),
            ('res_id', '=', inquiry.id),
            ('event_type', '=', 'INQUIRY_CLOSED'),
        ], limit=1))

    def test_10_plan_reserve(self):
        req = self._request()
        plan = self.env['pickup.plan'].create({
            'name': 'WF-PLAN',
            'transport_request_id': req.id,
            'scene_id': self.scene.id,
            'cargo_type': 'container',
            'destination_type': 'warehouse',
            'warehouse_id': self.wh.id,
        })
        plan.action_schedule()
        self.assertEqual(plan.state, 'scheduled')
        plan.action_reserve(reservation_type='vehicle')
        self.assertEqual(plan.state, 'reserved')
        self.assertEqual(plan.reservation_type, 'vehicle')
        self.assertTrue(plan.vehicle_allocation_snapshot)
        self.assertTrue(self.env['tlmp.transport.event.ledger'].search([
            ('res_model', '=', 'pickup.plan'),
            ('res_id', '=', plan.id),
            ('event_type', '=', 'PLAN_RESERVED'),
        ], limit=1))

    def test_11_vehicle_snapshot_guard(self):
        req = self._request()
        req.write({'vehicle_requirement_mode_snapshot': 'required'})
        quote = self.env['tlmp.transport.quote'].create({
            'request_id': req.id,
            'carrier_cost': 100.0,
        })
        with self.assertRaises(UserError):
            quote._auto_create_order()
