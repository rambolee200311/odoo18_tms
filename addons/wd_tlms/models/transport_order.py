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
        return super().create(vals_list)

    @api.depends('surcharge_ids.amount')
    def _compute_surcharge_total(self):
        for r in self:
            r.total_surcharge = sum(r.surcharge_ids.mapped('amount'))

    # ---- State Transitions ----
    def action_confirm(self):
        self.write({'state': 'confirmed'})
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
