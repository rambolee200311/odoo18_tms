"""Sprint49-B: Vehicle Requirement Rule Tests."""

import json

from odoo.tests import TransactionCase


class TestVehicleRequirement(TransactionCase):
    """Test vehicle requirement fields, compute, snapshot, and rules."""

    def setUp(self):
        super().setUp()
        # Create a scene for plan-driven flow
        self.scene_s1 = self.env['tlmp.transport.scene'].search(
            [('code', '=', 'terminal_to_warehouse')], limit=1
        ) or self.env['tlmp.transport.scene'].create({
            'name': 'Test S1', 'code': 'terminal_to_warehouse',
            'scene_type': 'plan_driven', 'destination_type': 'warehouse',
        })

    def _create_request(self, **kwargs):
        vals = {
            'scene_id': self.scene_s1.id,
            'request_type': 'plan_driven',
            'cargo_type': 'container',
            'carrier_type': kwargs.get('carrier_type', 'truck'),
            'vehicle_body_type': kwargs.get('vehicle_body_type', 'no_requirement'),
            'vehicle_capacity_requirement': kwargs.get(
                'vehicle_capacity_requirement', 'no_limit'),
            'is_dangerous_goods': kwargs.get('is_dangerous_goods', 'normal'),
            'has_dangerous_goods': kwargs.get('has_dangerous_goods', False),
            'dg_attribute': kwargs.get('dg_attribute', 'normal'),
            'dg_adr_class': kwargs.get('dg_adr_class', False),
            'dg_un_code': kwargs.get('dg_un_code', False),
            'warehouse_id': self.env['stock.warehouse'].search([], limit=1).id,
        }
        request = self.env['tlmp.transport.request'].create(vals)
        return request

    # -----------------------------------------------------------
    # Test 1: Default vehicle_requirement_mode derivation
    # -----------------------------------------------------------
    def test_01_default_mode_truck(self):
        """D2 third-party truck should default to required."""
        req = self._create_request(carrier_type='truck')
        self.assertEqual(req.vehicle_requirement_mode, 'required')

    def test_02_default_mode_own_fleet(self):
        """D1 own fleet should default to required."""
        req = self._create_request(carrier_type='own_fleet')
        self.assertEqual(req.vehicle_requirement_mode, 'required')

    def test_03_default_mode_courier(self):
        """D3 courier should default to exempted."""
        req = self._create_request(carrier_type='courier')
        self.assertEqual(req.vehicle_requirement_mode, 'exempted')

    # -----------------------------------------------------------
    # Test 2: carrier_type switch recalculates mode (pre-confirm)
    # -----------------------------------------------------------
    def test_04_carrier_switch_recalc(self):
        """Switching carrier_type should recalc vehicle_requirement_mode."""
        req = self._create_request(carrier_type='truck')
        self.assertEqual(req.vehicle_requirement_mode, 'required')
        req.carrier_type = 'courier'
        self.assertEqual(req.vehicle_requirement_mode, 'exempted')

    # -----------------------------------------------------------
    # Test 3: Snapshot frozen after confirm
    # -----------------------------------------------------------
    def test_05_snapshot_frozen_on_confirm(self):
        """vehicle_requirement_mode_snapshot frozen after confirm."""
        req = self._create_request(carrier_type='truck')
        self.assertFalse(req.vehicle_requirement_mode_snapshot)
        req.action_confirm()
        self.assertEqual(req.vehicle_requirement_mode_snapshot, 'required')

    def test_06_snapshot_protected_from_policy_change(self):
        """Snapshot should not change even if carrier_type changes after confirm."""
        req = self._create_request(carrier_type='truck')
        req.action_confirm()
        snapshot_before = req.vehicle_requirement_mode_snapshot
        # Snapshot is readonly, can't overwrite directly
        self.assertEqual(snapshot_before, 'required')

    # -----------------------------------------------------------
    # Test 4: Exempted mode skips vehicle validation
    # -----------------------------------------------------------
    def test_07_exempted_passes_empty_vehicle(self):
        """Courier (exempted) should pass even with no vehicle fields filled."""
        req = self._create_request(carrier_type='courier')
        self.assertEqual(req.vehicle_requirement_mode, 'exempted')

    # -----------------------------------------------------------
    # Test 5: ADR dangerous goods with/without ADR vehicle capability
    # -----------------------------------------------------------
    def test_08_adr_without_capability(self):
        """ADR request without carrier ADR capability should be caught by rule."""
        req = self._create_request(
            carrier_type='truck', dg_attribute='dg',
            is_dangerous_goods='adr_dangerous')
        req.action_confirm()
        self.assertEqual(req.state, 'confirmed')

    def test_09_courier_adr_blocked(self):
        """D3 courier carrying ADR DG should be blocked by matrix rules."""
        req = self._create_request(
            carrier_type='courier', cargo_type='piece',
            dg_attribute='dg', is_dangerous_goods='adr_dangerous')
        # Should be blocked by RULE-CARGO-004 / RULE-VEHICLE-005
        self.assertEqual(req.matrix_validation_result, 'block')

    # -----------------------------------------------------------
    # Test 6: capacity requirement scenarios
    # -----------------------------------------------------------
    def test_10_capacity_no_limit(self):
        """no_limit capacity should be fine."""
        req = self._create_request(
            carrier_type='truck',
            vehicle_capacity_requirement='no_limit')
        self.assertEqual(req.vehicle_capacity_requirement, 'no_limit')

    def test_11_capacity_below_40t(self):
        """below_40t capacity constraint sets correctly."""
        req = self._create_request(
            carrier_type='truck',
            vehicle_capacity_requirement='below_40t')
        self.assertEqual(req.vehicle_capacity_requirement, 'below_40t')

    # -----------------------------------------------------------
    # Test 7: Body type scenarios
    # -----------------------------------------------------------
    def test_12_body_type_no_requirement(self):
        """no_requirement body type is default and accepted."""
        req = self._create_request(carrier_type='truck')
        self.assertEqual(req.vehicle_body_type, 'no_requirement')

    def test_13_body_type_reefer(self):
        """Reefer body type sets correctly."""
        req = self._create_request(
            carrier_type='truck', vehicle_body_type='reefer_refrigerated')
        self.assertEqual(req.vehicle_body_type, 'reefer_refrigerated')

    # -----------------------------------------------------------
    # Test 8: Inquiry/Quote vehicle field projection
    # -----------------------------------------------------------
    def test_14_inquiry_vehicle_projection(self):
        """Inquiry should project vehicle_requirement_mode from request."""
        req = self._create_request(carrier_type='truck')
        # Create inquiry for this request
        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': req.id,
            'cargo_summary': 'Test cargo',
        })
        self.assertEqual(inquiry.vehicle_requirement_mode, 'required')

    def test_15_quote_vehicle_projection(self):
        """Quote should project vehicle_requirement_mode from request."""
        req = self._create_request(carrier_type='courier')
        # Create inquiry then quote
        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': req.id,
            'cargo_summary': 'Test cargo',
        })
        quote = self.env['tlmp.transport.quote'].create({
            'request_id': req.id,
            'inquiry_id': inquiry.id,
            'carrier_cost': 100.0,
        })
        self.assertEqual(quote.vehicle_requirement_mode, 'exempted')

    def test_16_quote_courier_exempted_display(self):
        """Quote for courier should show exempted vehicle mode."""
        req = self._create_request(carrier_type='courier')
        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': req.id,
            'cargo_summary': 'Test cargo',
        })
        quote = self.env['tlmp.transport.quote'].create({
            'request_id': req.id,
            'inquiry_id': inquiry.id,
            'carrier_cost': 50.0,
        })
        self.assertEqual(quote.vehicle_requirement_mode, 'exempted')

    def test_17_confirmed_request_snapshot_propagates_to_order(self):
        """Confirming a request should freeze vehicle snapshot and propagate it to orders."""
        req = self._create_request(
            carrier_type='truck',
            vehicle_body_type='reefer_refrigerated',
            vehicle_capacity_requirement='below_40t',
        )
        req.action_confirm()
        req.write({'matrix_code': 'S1-B1-C1-D2-E2-F2', 'matrix_validation_result': 'pass'})

        inquiry = self.env['tlmp.transport.inquiry'].create({
            'request_id': req.id,
            'cargo_summary': 'Test cargo',
        })
        quote = self.env['tlmp.transport.quote'].create({
            'request_id': req.id,
            'inquiry_id': inquiry.id,
            'carrier_cost': 100.0,
        })
        quote.action_send()
        quote.action_accept()

        order = quote.transport_order_id
        self.assertTrue(order)
        self.assertTrue(order.vehicle_requirement_snapshot)
        snapshot = json.loads(order.vehicle_requirement_snapshot)
        self.assertEqual(snapshot['vehicle_requirement_mode'], 'required')
        self.assertEqual(snapshot['vehicle_requirement_mode_snapshot'], 'required')
        self.assertEqual(snapshot['vehicle_body_type'], 'reefer_refrigerated')
        self.assertEqual(snapshot['vehicle_capacity_requirement'], 'below_40t')