# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PickupPlan(models.Model):
    _name = 'pickup.plan'
    _description = 'Pickup Requirement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(string='Requirement No.', required=True, copy=False,
                       default=lambda self: _('New'))

    # ---- Source ----
    source_type = fields.Selection([
        ('iff', 'From IFF (wd_iffm)'),
        ('manual', 'Manual Entry'),
    ], string='Source', default='manual', required=True)

    iff_requirement_ref = fields.Reference(
        selection=lambda self: self._get_reference_models(),
        string='IFF Pickup Requirement',
        help='Reference to the pickup requirement from Import Freight Forwarding (wd_iffm)',
    )

    # ---- Container lines ----
    container_line_ids = fields.One2many(
        'pickup.plan.container.line', 'plan_id',
        string='Containers', copy=True)
    is_bonded_transfer = fields.Boolean(
        string='Bonded Transfer',
        help='If checked, triggers bonded warehouse accounting (B3/T1) on transfer')

    iff_plan_ref_id = fields.Integer(
        string='IFF Plan Ref ID',
        help='Internal ID of the source import.pickup.requirement for read-only enforcement')

    # ---- Cargo type ----
    cargo_type = fields.Selection([
        ('container', 'Container'),
        ('pallet', 'Pallet / Piece'),
    ], string='Cargo Type', required=True, default='container')

    # ---- Destination (determines downstream flow) ----
    destination_type = fields.Selection([
        ('warehouse', 'Terminal / Depot to Our Warehouse'),
        ('warehouse_transfer', 'Our Warehouse Transfer'),
        ('customer', 'Terminal / Depot to Customer'),
        ('self_pickup', 'Customer Self-Pickup'),
    ], string='Destination', required=True, default='warehouse',
        help='Warehouse/Warehouse Transfer → Plan → Order. Other → Inquiry → Quote → Order')

    terminal_id = fields.Many2one(
        'res.partner', string='Origin Terminal / Port',
        domain=[('is_company', '=', True)],
        help='Terminal, depot or port where the container is picked up')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Destination Warehouse',
        help='Where the goods are going (required for warehouse destination)')
    source_warehouse_id = fields.Many2one(
        'stock.warehouse', string='Source Warehouse',
        help='Origin warehouse for warehouse transfer scenario')
    delivery_address = fields.Text(string='Delivery Address')
    delivery_contact = fields.Char(string='Delivery Contact')
    delivery_phone = fields.Char(string='Delivery Phone')

    # ---- Pallet / Piece cargo fields ----
    pallet_count = fields.Integer(string='Pallets')
    package_count = fields.Integer(string='Packages')
    cargo_weight = fields.Float(string='Weight (kg)', digits='Stock Weight')
    cargo_volume = fields.Float(string='Volume (m3)', digits='Volume')
    cargo_description = fields.Text(string='Cargo Description')

    # ---- Scheduling (filled during calendar scheduling) ----
    carrier_id = fields.Many2one(
        'res.partner', string='Trucking Company',
        domain=[('is_carrier', '=', True)],
        help='Default carrier from system parameter tlmp.default_pickup_carrier_id')
    planned_pickup_date = fields.Datetime(string='Planned Pickup')

    driver_name = fields.Char(string='Driver Name')
    driver_phone = fields.Char(string='Driver Phone')
    vehicle_plate = fields.Char(string='Vehicle Plate')

    # ---- Customer (needed for inquiry flow) ----
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        domain=[('is_company', '=', True)],
        help='Customer who needs this transport (for non-warehouse flow)')

    # ---- Links ----
    transport_request_id = fields.Many2one(
        'tlmp.transport.request', string='Transport Request',
        readonly=True, copy=False)
    inquiry_id = fields.Many2one(
        'tlmp.transport.inquiry', string='Inquiry', readonly=True, copy=False)
    transport_order_id = fields.Many2one(
        'tlmp.transport.order', string='Transport Order', readonly=True, copy=False)

    notes = fields.Text(string='Notes')
    scheduled_date = fields.Date(string='Scheduled Date', index=True,
        help='Date assigned via Schedule calendar. Used for warehouse / warehouse_transfer destinations.')
    schedule_ids = fields.One2many(
        'schedule.plan.schedule', 'plan_id',
        string='Schedules', copy=False,
        help='Schedule records associated with this pick-up plan. Each record represents a container or pallet scheduled on a specific date.')

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    # -----------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------
    @api.model
    def _get_reference_models(self):
        models = []
        if self.env.get('import.pickup.requirement'):
            models.append(('import.pickup.requirement', 'Import Pickup Requirement'))
        return models

    # -----------------------------------------------------------
    # Default carrier from system parameter
    # -----------------------------------------------------------
    @api.model
    def _default_carrier_id(self):
        carrier_id = self.env['ir.config_parameter'].sudo().get_param(
            'tlmp.default_pickup_carrier_id', default=False)
        return carrier_id and int(carrier_id) or False

    # -----------------------------------------------------------
    # Onchange: auto-load containers & metadata from iff requirement
    # -----------------------------------------------------------
    @api.onchange('iff_requirement_ref')
    def _onchange_iff_requirement_ref(self):
        if not self.iff_requirement_ref:
            self.container_line_ids = [(5, 0, 0)]
            return
        req = self.iff_requirement_ref
        if req._name != 'import.pickup.requirement' or not req.container_lines:
            return

        # Map IFF pickup scene to destination
        self.terminal_id = req.terminal_a if hasattr(req, 'terminal_a') else False
        if req.pickup_scene == 'to_our_warehouse' and req.warehouse_id:
            self.destination_type = 'warehouse'
            self.warehouse_id = req.warehouse_id
        elif req.pickup_scene == 'to_customer_address':
            self.destination_type = 'customer'
            self.delivery_address = (
                (req.delivery_street or '') + ', ' +
                (req.delivery_zip or '') + ' ' +
                (req.delivery_city or ''))
            self.delivery_contact = req.delivery_contact_id.display_name if req.delivery_contact_id else ''
            self.delivery_phone = req.delivery_phone or ''
        elif req.pickup_scene == 'customer_self_pickup':
            self.destination_type = 'self_pickup'
            self.delivery_contact = req.self_pickup_contact_id.display_name if req.self_pickup_contact_id else ''
            self.delivery_phone = req.self_pickup_phone or ''

        lines = []
        for cl in req.container_lines:
            lines.append((0, 0, {
                'container_number': cl.container_number,
                'container_type': cl.container_type or '20GP',
                'weight': cl.weight,
            }))
        self.container_line_ids = lines

    # -----------------------------------------------------------
    # Validate: bonded transfer required when source or dest is bonded warehouse
    # -----------------------------------------------------------
    @api.constrains('destination_type', 'is_bonded_transfer', 'warehouse_id', 'source_warehouse_id')
    def _check_bonded_transfer(self):
        for rec in self:
            if rec.destination_type != 'warehouse_transfer':
                continue
            warehouses = rec.source_warehouse_id + rec.warehouse_id
            is_bonded = any(warehouse.is_bonded_warehouse if hasattr(warehouse, 'is_bonded_warehouse') else False
                            for warehouse in warehouses)
            if is_bonded and not rec.is_bonded_transfer:
                raise UserError(
                    _('Bonded Transfer must be checked when one of the warehouses is a bonded warehouse.'))

    # -----------------------------------------------------------
    # Validate: partner_id required for customer/self_pickup
    # -----------------------------------------------------------
    @api.constrains('destination_type', 'partner_id')
    def _check_partner_required(self):
        for rec in self:
            if rec.destination_type in ('customer', 'self_pickup') and not rec.partner_id:
                raise UserError(
                    _('Customer is required for customer delivery or self-pickup destinations.'))

    # -----------------------------------------------------------
    # Validate: warehouse_id required for warehouse / warehouse_transfer
    # -----------------------------------------------------------
    @api.constrains('destination_type', 'warehouse_id')
    def _check_warehouse_required(self):
        for rec in self:
            if rec.destination_type in ('warehouse', 'warehouse_transfer') and not rec.warehouse_id:
                raise UserError(
                    _('Destination Warehouse is required for warehouse or warehouse transfer destinations.'))

    # -----------------------------------------------------------
    # Validate: source_warehouse_id required for warehouse_transfer
    # -----------------------------------------------------------
    @api.constrains('destination_type', 'source_warehouse_id')
    def _check_source_warehouse_required(self):
        for rec in self:
            if rec.destination_type == 'warehouse_transfer' and not rec.source_warehouse_id:
                raise UserError(
                    _('Source Warehouse is required for warehouse transfer destinations.'))


    # -----------------------------------------------------------
    # Write: enforce bonded transfer validation + carrier default
    # -----------------------------------------------------------
    def write(self, vals):
        # Enforce bonded transfer check before save
        for rec in self:
            new_vals = vals.copy()
            if 'destination_type' not in new_vals:
                new_vals['destination_type'] = rec.destination_type
            if 'is_bonded_transfer' not in new_vals:
                new_vals['is_bonded_transfer'] = rec.is_bonded_transfer
            if 'warehouse_id' not in new_vals:
                new_vals['warehouse_id'] = rec.warehouse_id.id if rec.warehouse_id else False
            if 'source_warehouse_id' not in new_vals:
                new_vals['source_warehouse_id'] = rec.source_warehouse_id.id if rec.source_warehouse_id else False

            if new_vals['destination_type'] == 'warehouse_transfer':
                w_ids = []
                if new_vals['warehouse_id']:
                    w_ids.append(new_vals['warehouse_id'])
                if new_vals['source_warehouse_id']:
                    w_ids.append(new_vals['source_warehouse_id'])
                if w_ids:
                    warehouses = self.env['stock.warehouse'].browse(w_ids)
                    is_bonded = any(
                        warehouse.is_bonded_warehouse if hasattr(warehouse, 'is_bonded_warehouse') else False
                        for warehouse in warehouses)
                    if is_bonded and not new_vals['is_bonded_transfer']:
                        raise UserError(
                            _('Bonded Transfer must be checked when one of the warehouses is a bonded warehouse.'))
        return super().write(vals)

    # -----------------------------------------------------------
    # Action: Create Transport Request (non-warehouse flow)
    # -----------------------------------------------------------
    def action_create_transport_request(self):
        self.ensure_one()
        if self.transport_request_id:
            return self._open_record(
                'tlmp.transport.request', self.transport_request_id.id)

        # Map destination_type to transport_type
        type_map = {
            'customer': 'to_customer',
            'self_pickup': 'to_customer',
        }
        tr_type = type_map.get(self.destination_type, 'to_customer')

        # For reverse logistics (return to warehouse), check if destination is actually back to us
        # Scene 6: Customer → Our Warehouse -> reverse_logistics
        # Determined by: destination_type=customer but warehouse_id is set
        if self.destination_type == 'customer' and self.warehouse_id:
            tr_type = 'reverse_logistics'

        container_nums = ', '.join(
            self.container_line_ids.mapped('container_number'))
        total_weight = sum(self.container_line_ids.mapped('weight'))
        container_count = len(self.container_line_ids)

        request = self.env['tlmp.transport.request'].create({
            'transport_type': tr_type,
            'partner_id': self.partner_id.id or self.env.user.partner_id.id,
            'customer_ref': self.name,
            'cargo_description':
                _('Port pickup - %s') % container_nums
                if container_nums else _('Port pickup'),
            'cargo_weight': total_weight or self.cargo_weight,
            'cargo_volume': self.cargo_volume,
            'pallet_count': self.pallet_count,
            'package_count': container_count or self.package_count,
            'special_requirements': self.notes,
        })

        self.transport_request_id = request.id
        return self._open_record('tlmp.transport.request', request.id)

    # -----------------------------------------------------------
    # Action: Create Transport Order directly (plan-driven flow)
    #   Scenes 1, 5: Terminal→Warehouse, Warehouse Transfer
    # -----------------------------------------------------------
    def action_create_transport_order(self):
        self.ensure_one()
        if self.transport_order_id:
            return self._open_record('tlmp.transport.order', self.transport_order_id.id)

        # Validate
        if self.destination_type not in ('warehouse', 'warehouse_transfer'):
            raise UserError(
                _('Direct order creation is only available for warehouse / warehouse transfer destinations. '
                  'For customer destinations, use "Create Transport Request" to go through the inquiry & quote flow.'))

        if self.cargo_type == 'container' and not self.container_line_ids:
            raise UserError(_('No container lines. Please add at least one container.'))

        if not self.carrier_id:
            # Fall back to default carrier from system parameter
            default_carrier = self._default_carrier_id()
            if default_carrier:
                self.carrier_id = default_carrier
            if not self.carrier_id:
                raise UserError(_('Please select a Trucking Company.'))

        type_map = {
            'warehouse': 'port_to_warehouse',
            'warehouse_transfer': 'warehouse_transfer',
        }
        tr_type = type_map.get(self.destination_type, 'port_to_warehouse')

        order_vals = {
            'transport_type': tr_type,
            'fleet_operation_mode': 'subcontracted',
            'partner_id': self.carrier_id.id or self.env.user.partner_id.id,
            'carrier_id': self.carrier_id.id,
            'cargo_description': self.cargo_description or (
                _('Pickup plan %s') % self.name),
            'cargo_weight': self.cargo_weight,
            'cargo_volume': self.cargo_volume,
            'pallet_count': self.pallet_count,
            'package_count': self.package_count,
            'planned_pickup_date': self.planned_pickup_date or self.scheduled_date,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'vehicle_plate': self.vehicle_plate,
            'notes': self.notes,
        }

        if self.destination_type == 'warehouse_transfer':
            order_vals['pickup_location_id'] = (
                self.source_warehouse_id.partner_id.id if self.source_warehouse_id else False)
            order_vals['delivery_location_id'] = (
                self.warehouse_id.partner_id.id if self.warehouse_id else False)
        else:
            order_vals['delivery_location_id'] = (
                self.warehouse_id.partner_id.id if self.warehouse_id else False)
            if self.terminal_id:
                order_vals['pickup_location_id'] = self.terminal_id.id

        # Source amounts from inquiry/quote if available, otherwise manual
        if self.inquiry_id and self.inquiry_id.state == 'accepted':
            order_vals['total_carrier_cost'] = self.inquiry_id.total_amount
            order_vals['source_amount_carrier'] = self.inquiry_id.total_amount
            order_vals['price_source'] = 'inquiry'
        else:
            order_vals['price_source'] = 'manual'

        order = self.env['tlmp.transport.order'].create(order_vals)

        # Create container lines on the order
        for cl in self.container_line_ids:
            self.env['tlmp.transport.container'].create({
                'order_id': order.id,
                'name': cl.container_number,
                'container_type': cl.container_type,
                'seal_number': cl.seal_number,
                'cargo_weight_kg': cl.weight,
                'container_master_id': cl.container_master_id.id,
            })

        self.transport_order_id = order.id
        return self._open_record('tlmp.transport.order', order.id)

    # -----------------------------------------------------------
    # Action: Open Schedule page (warehouse flow)
    # -----------------------------------------------------------
    def action_open_schedule(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/pickup_schedule',
            'target': 'self',
        }

    def _open_record(self, model, res_id):
        return {
            'type': 'ir.actions.act_window',
            'res_model': model,
            'view_mode': 'form',
            'res_id': res_id,
            'target': 'current',
        }

    # -----------------------------------------------------------
    # Sequence
    # -----------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'pickup.plan.seq') or _('New')
        return super().create(vals_list)


class PickupPlanContainerLine(models.Model):
    _name = 'pickup.plan.container.line'
    _description = 'Pickup Plan Container'
    _order = 'id'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if r.container_number and not r.container_master_id:
                master, _ = self.env['container.master'].find_or_create(
                    r.container_number, r.container_type)
                r.container_master_id = master.id
                self.env['container.master.history.line'].create({
                    'master_id': master.id,
                    'reference_type': 'pickup_plan',
                    'reference_id': r.plan_id.id if r.plan_id else 0,
                    'bl_number': r.bl_number,
                    'direction': 'inbound',
                    'remark': 'Container from pickup plan',
                })
            # Auto-create bl.container for schedule page
            if r.container_number:
                plan = r.plan_id
                existing_bl_no = r.bl_number
                if not existing_bl_no and plan:
                    existing_bl_no = plan.bl_number if 'bl_number' in plan._fields else ''
                existing = self.env['bl.container'].search(
                    [('container_no', '=', r.container_number)], limit=1)
                if not existing:
                    self.env['bl.container'].create({
                        'container_no': r.container_number,
                        'container_type': r.container_type or '20GP',
                        'bl_no': r.bl_number or existing_bl_no or '',
                        'destination_warehouse': plan.warehouse_id.id if plan and plan.warehouse_id else False,
                        'state': 'pending',
                    })
        return res

    # -----------------------------------------------------------
    # Write protection: IFFM-sourced records are read-only for container detail fields
    # -----------------------------------------------------------
    def write(self, vals):
        iff_protected = ['container_number', 'container_type', 'weight',
                         'bl_number', 'seal_number']
        for rec in self:
            plan = rec.plan_id
            if plan and plan.source_type == 'iff' and any(k in vals for k in iff_protected):
                raise UserError(
                    _('Cannot modify container details on IFFM-sourced requirements. '
                      'Please modify the source in IFFM module.'))
        return super().write(vals)

    plan_id = fields.Many2one(
        'pickup.plan', string='Plan', required=True,
        ondelete='cascade', index=True)
    container_number = fields.Char(string='Container No.', required=True)
    container_type = fields.Selection([
        ('20GP', '20GP'), ('40GP', '40GP'), ('40HQ', '40HQ'),
        ('40HC', '40HC'), ('45HQ', '45HQ'), ('OT', 'OT'),
        ('FR', 'FR'), ('RF', 'RF'), ('other', 'Other'),
    ], string='Container Type', default='20GP')
    weight = fields.Float(string='Weight (kg)')
    seal_number = fields.Char(string='Seal No.')
    container_master_id = fields.Many2one('container.master', string='Container Record',
                                          ondelete='set null', index=True)
    bl_number = fields.Char(string='BL No.',
                            help='Bill of Lading number from the original waybill')
    notes = fields.Text(string='Notes')