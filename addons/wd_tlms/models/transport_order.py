# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TransportOrder(models.Model):
    _name = 'tlmp.transport.order'
    _description = 'Transport Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Order No.', required=True, copy=False,
                       default=lambda self: _('New'))
    transport_type = fields.Selection([
        ('port_to_warehouse', 'Terminal to Warehouse'),
        ('to_customer', 'To Customer'),
        ('pickup_to_warehouse', 'Pickup to Warehouse'),
        ('warehouse_transfer', 'Warehouse Transfer'),
        ('reverse_logistics', 'Reverse Logistics'),
    ], string='Transport Type', required=True)
    fleet_operation_mode = fields.Selection([
        ('own_fleet', 'Own Fleet'),
        ('contracted', 'Contracted'),
        ('subcontracted', 'Subcontracted'),
    ], string='Fleet Mode', required=True, default='subcontracted')
    request_id = fields.Many2one('tlmp.transport.request', string='Request')
    quote_id = fields.Many2one('tlmp.transport.quote', string='Quote')
    inquiry_id = fields.Many2one('tlmp.transport.inquiry', string='Inquiry')
    pickup_plan_id = fields.Many2one(
        'pickup.plan', string='Pickup Plan',
        readonly=True, copy=False, index=True,
        help='Source document for plan-driven flow.')
    source_type = fields.Selection([
        ('plan_driven', 'Plan-Driven'),
        ('commercial', 'Commercial'),
    ], string='Source Type', compute='_compute_source_type', store=True)

    @api.depends('pickup_plan_id', 'quote_id', 'request_id')
    def _compute_source_type(self):
        for r in self:
            if r.pickup_plan_id:
                r.source_type = 'plan_driven'
            elif r.quote_id:
                r.source_type = 'commercial'
            elif r.request_id and r.request_id.request_type:
                r.source_type = r.request_id.request_type
            else:
                r.source_type = False

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    carrier_id = fields.Many2one('res.partner', string='Carrier', required=True)
    carrier_contact = fields.Char(string='Carrier Contact')
    carrier_phone = fields.Char(string='Carrier Phone')
    pickup_location_id = fields.Many2one('res.partner', string='Pickup Location')
    delivery_location_id = fields.Many2one('res.partner', string='Delivery Location')
    planned_pickup_date = fields.Datetime(string='Planned Pickup')
    planned_delivery_date = fields.Datetime(string='Planned Delivery')
    actual_pickup_date = fields.Datetime(string='Actual Pickup')
    actual_delivery_date = fields.Datetime(string='Actual Delivery')
    driver_name = fields.Char(string='Driver')
    driver_phone = fields.Char(string='Driver Phone')
    vehicle_plate = fields.Char(string='Vehicle Plate')
    cargo_description = fields.Text(string='Cargo')
    cargo_weight = fields.Float(string='Weight (kg)')
    cargo_volume = fields.Float(string='Volume (m3)')
    pallet_count = fields.Integer(string='Pallets')
    package_count = fields.Integer(string='Packages')
    container_ids = fields.One2many('tlmp.transport.container', 'order_id', string='Containers')
    surcharge_ids = fields.One2many('tlmp.surcharge', 'order_id', string='Surcharges')
    total_base_fee = fields.Monetary(string='Base Fee')
    total_surcharge = fields.Monetary(string='Total Surcharge', compute='_compute_surcharge_total')
    total_carrier_cost = fields.Monetary(string='Carrier Cost')
    total_customer_charge = fields.Monetary(string='Customer Charge')
    source_amount_carrier = fields.Monetary(string='Source Amt (Carrier)', readonly=True)
    source_amount_customer = fields.Monetary(string='Source Amt (Customer)', readonly=True)
    price_source = fields.Selection([
        ('quote', 'From Quote'),
        ('inquiry', 'From Inquiry'),
        ('pricing_rule', 'Pricing Rule'),
        ('manual', 'Manual'),
        ('carrier_api', 'Carrier API'),
    ], string='Price Source', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    customer_bill_id = fields.Many2one('tlmp.customer.bill', string='Customer Bill', readonly=True)
    carrier_settlement_id = fields.Many2one('tlmp.carrier.settlement', string='Carrier Settlement',
                                            readonly=True)
    cmr_ids = fields.One2many('tlmp.cmr', 'order_id', string='CMR Documents')
    pod_id = fields.Many2one('tlmp.pod', string='POD', readonly=True)
    trip_id = fields.Many2one('container.transport.plan', string='Trip Plan', index=True)
    settlement_locked = fields.Boolean(string='Settlement Locked', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('signed', 'Signed'),
        ('billed', 'Billed'),
        ('settled', 'Settled'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    has_dangerous_goods = fields.Boolean(string='DG', default=False)
    adr_un_number = fields.Char(string='UN No.')
    adr_class = fields.Char(string='ADR Class')
    adr_packing_group = fields.Selection([('I', 'I'), ('II', 'II'), ('III', 'III'),
                                          ('none', 'N/A')], string='PG')
    adr_tunnel_code = fields.Selection([
        ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
        ('B/D', 'B/D'), ('C/D', 'C/D'), ('D/E', 'D/E'),
    ], string='Tunnel Code')
    customs_transit_ref = fields.Char(string='T1 MRN')
    customs_declaration_ref = fields.Char(string="Customs Decl. Ref.")
    t1_state = fields.Selection([
        ('none', 'None'),
        ('declared', 'Declared'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('closed', 'Closed'),
    ], string='T1 State', default='none')
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('tlmp.order.seq') or _('New')
            # Safety defaults for required fields
            if not vals.get('partner_id'):
                partner = self.env['res.partner'].create({'name': 'System Partner'})
                vals['partner_id'] = partner.id
            if not vals.get('carrier_id'):
                carrier = self.env['res.partner'].create({'name': 'System Carrier'})
                vals['carrier_id'] = carrier.id
            if not vals.get('transport_type'):
                vals['transport_type'] = 'port_to_warehouse'
            if not vals.get('fleet_operation_mode'):
                vals['fleet_operation_mode'] = 'subcontracted'
        return super().create(vals_list)

    @api.depends('surcharge_ids.amount')
    def _compute_surcharge_total(self):
        for r in self:
            r.total_surcharge = sum(r.surcharge_ids.mapped('amount'))

    # -----------------------------------------------------------
    # Upstream status sync
    # -----------------------------------------------------------
    def _sync_upstream_status(self):
        """Sync order status back to upstream documents."""
        for r in self:
            # Plan-driven: update pickup.plan state
            if r.pickup_plan_id:
                r.pickup_plan_id.scheduled_date = r.planned_pickup_date.date() if r.planned_pickup_date else r.pickup_plan_id.scheduled_date
            # Commercial: ensure quote is marked accepted
            if r.quote_id and r.quote_id.state != 'accepted':
                r.quote_id.sudo().write({'state': 'accepted'})

    # -----------------------------------------------------------
    # Dual-source creation assistant
    # -----------------------------------------------------------
    @api.model
    def create_from_pickup_plan(self, pickup_plan):
        """Create transport.order from a pickup.plan (plan-driven flow)."""
        type_map = {'warehouse': 'port_to_warehouse', 'warehouse_transfer': 'warehouse_transfer',
                    'customer': 'to_customer', 'self_pickup': 'to_customer'}
        tr_type = type_map.get(pickup_plan.destination_type, 'port_to_warehouse')
        val = {
            'transport_type': tr_type,
            'fleet_operation_mode': 'subcontracted',
            'pickup_plan_id': pickup_plan.id,
            'request_id': pickup_plan.transport_request_id.id if pickup_plan.transport_request_id else False,
            'partner_id': pickup_plan.partner_id.id or pickup_plan.carrier_id.id or False,
            'carrier_id': pickup_plan.carrier_id.id if pickup_plan.carrier_id else False,
            'cargo_description': pickup_plan.cargo_description or '',
            'cargo_weight': pickup_plan.cargo_weight,
            'cargo_volume': pickup_plan.cargo_volume,
            'pallet_count': pickup_plan.pallet_count,
            'package_count': pickup_plan.package_count,
            'planned_pickup_date': pickup_plan.planned_pickup_date or pickup_plan.scheduled_date,
            'driver_name': pickup_plan.driver_name,
            'driver_phone': pickup_plan.driver_phone,
            'vehicle_plate': pickup_plan.vehicle_plate,
            'notes': pickup_plan.notes,
        }
        if pickup_plan.destination_type == 'warehouse_transfer':
            val['pickup_location_id'] = pickup_plan.source_warehouse_id.partner_id.id if pickup_plan.source_warehouse_id else False
            val['delivery_location_id'] = pickup_plan.warehouse_id.partner_id.id if pickup_plan.warehouse_id else False
        else:
            val['delivery_location_id'] = pickup_plan.warehouse_id.partner_id.id if pickup_plan.warehouse_id else False
            if pickup_plan.terminal_id:
                val['pickup_location_id'] = pickup_plan.terminal_id.id
        order = self.create(val)
        # Copy container lines
        for cl in pickup_plan.container_line_ids:
            self.env['tlmp.transport.container'].create({
                'order_id': order.id, 'name': cl.container_number,
                'container_type': cl.container_type, 'seal_number': cl.seal_number,
                'cargo_weight_kg': cl.weight,
                'container_master_id': cl.container_master_id.id if cl.container_master_id else False,
            })
        return order

    # ---- State Transitions ----
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        self._sync_upstream_status()
        return True

    def action_assign(self):
        self.write({'state': 'assigned'})
        return True

    def action_start_transit(self):
        self.write({'state': 'in_transit', 'actual_pickup_date': fields.Datetime.now()})
        return True

    def action_deliver(self):
        self.write({'state': 'delivered', 'actual_delivery_date': fields.Datetime.now()})
        return True

    def action_confirm_pod(self):
        self.write({'state': 'signed'})
        # Update container history: record return date
        HistoryLine = self.env['container.master.history.line']
        for container in self.container_ids:
            if not container.container_master_id:
                continue
            # Find the most recent inbound history line for this master
            hist = HistoryLine.search([
                ('master_id', '=', container.container_master_id.id),
                ('return_date', '=', False),
            ], limit=1, order='id desc')
            if hist:
                hist.write({
                    'return_date': fields.Date.today(),
                    'location_end': self.delivery_location_id.name if self.delivery_location_id else False,
                })
        return True

    def action_bill(self):
        lock = self._check_settle_lock()
        if lock['locked']:
            raise UserError(_('Cannot bill: %s') % lock['reason'])
        self.write({'state': 'billed'})
        return True

    def action_settle(self):
        lock = self._check_settle_lock()
        if lock['locked']:
            raise UserError(_('Cannot settle: %s') % lock['reason'])
        self.write({'state': 'settled'})
        return True

    def action_close(self):
        self.ensure_one()
        if not self.pod_id or self.pod_id.state != 'confirmed':
            raise UserError(_('Cannot close order: POD must be confirmed first.'))
        self.write({'state': 'closed'})
        return True

    def action_cancel(self, reason=None):
        self.write({'state': 'cancelled'})
        return True

    def action_reject(self, reason=None):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Only confirmed orders can be rejected to draft.'))
        self.write({'state': 'draft'})
        return True

    def action_void(self, reason=None):
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True

    # ---- Settlement Lock ----
    def _check_settle_lock(self):
        self.ensure_one()
        pod_confirmed = self.pod_id and self.pod_id.state == 'confirmed'
        cmr_exists = bool(self.cmr_ids)
        cmr_signed = any(c.state == 'signed' for c in self.cmr_ids)
        if not pod_confirmed:
            return {'locked': True, 'reason': 'POD not confirmed'}
        if cmr_exists and not cmr_signed:
            return {'locked': True, 'reason': 'CMR not signed'}
        if self.pod_id.state in ('disputed',):
            return {'locked': True, 'reason': 'POD has unresolved dispute'}
        if self.pod_id.goods_condition in ('damaged', 'short', 'rejected'):
            return {'locked': True, 'reason': 'POD has damage/short/rejected issue'}
        if self.settlement_locked:
            return {'locked': True, 'reason': 'Order is locked (damage/claim pending)'}
        return {'locked': False}

    def compute_pricing(self):
        self.ensure_one()
        # Priority 1: Inherit from accepted quote
        if self.quote_id and self.quote_id.state == 'accepted':
            self.total_customer_charge = self.quote_id.total_amount
            self.source_amount_customer = self.quote_id.total_amount
            if self.inquiry_id:
                self.total_carrier_cost = self.inquiry_id.total_amount
                self.source_amount_carrier = self.inquiry_id.total_amount
            self.price_source = 'quote'
            return True
        # Priority 2: Inherit from inquiry
        if self.inquiry_id and self.inquiry_id.state == 'accepted':
            self.total_carrier_cost = self.inquiry_id.total_amount
            self.source_amount_carrier = self.inquiry_id.total_amount
            margin = float(self.env['ir.config_parameter'].sudo().get_param(
                'tlmp.service_margin_rate', default=0.15))
            self.total_customer_charge = self.total_carrier_cost * (1 + margin)
            self.source_amount_customer = self.total_customer_charge
            self.price_source = 'inquiry'
            return True
        # Priority 3: Use pricing rules
        rules = self.env['tlmp.pricing.rule'].search([
            ('active', '=', True),
            ('transport_type', '=', self.transport_type),
            ('carrier_type', '=', self.fleet_operation_mode),
        ], order='priority asc', limit=1)
        if rules:
            rule = rules[0]
            self.price_source = 'pricing_rule'
            # Apply the first matching tier
            tier = rule.line_ids.filtered(
                lambda l: (not l.min_value or self.cargo_weight >= l.min_value)
                and (not l.max_value or self.cargo_weight <= l.max_value)
            )
            if tier:
                self.total_carrier_cost = tier[0].base_fee + (tier[0].unit_price * self.cargo_weight)
                self.source_amount_carrier = self.total_carrier_cost
                margin = float(self.env['ir.config_parameter'].sudo().get_param(
                    'tlmp.service_margin_rate', default=0.15))
                self.total_customer_charge = self.total_carrier_cost * (1 + margin)
                self.source_amount_customer = self.total_customer_charge
        else:
            self.price_source = 'manual'
        return True
