# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from ..business_matrix.rule_engine import BusinessMatrixEngine
from ..business_matrix.rule_definition import (
    SCENE_S_CODES, BUSINESS_DRIVER, CARGO_CATEGORY,
    CARRIER_TYPE, T1_ATTRIBUTE, DG_ATTRIBUTE)


class TransportRequest(models.Model):
    _name = 'tlmp.transport.request'

    _name = 'tlmp.transport.request'
    _description = 'Transport Request (Unified Entry Point)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'
    _rec_name = 'name'
        # ---- Identity ----
    name = fields.Char(string='Request No.', required=True, copy=False,
                      default=lambda self: _('New'))
    scene_code = fields.Char(related='scene_id.code', string='Scene Code', store=True, readonly=True)
    scene_id = fields.Many2one('tlmp.transport.scene', string='Transport Scene',
                               help='Sprint40: scene becomes the primary business dimension. Replaces old request_type+destination_type two-dimensional flow model.')

    # ---- Flow Control (determines downstream path) ----
    request_type = fields.Selection([
       ('plan_driven', 'Plan-Driven'),
       ('commercial', 'Commercial'),
    ], string='Request Type', required=True, default='plan_driven',
       help='Plan-Driven: Schedule + pickup.plan + order. Commercial: Inquiry + Quote + order.')

    destination_type = fields.Selection([
       ('warehouse', 'Terminal / Depot to Our Warehouse'),
       ('warehouse_transfer', 'Our Warehouse Transfer'),
       ('customer', 'Terminal / Depot to Customer'),
       ('self_pickup', 'Customer Self-Pickup'),
    ], string='Destination', required=True, default='warehouse',
       help='Aligns with IFFM import.pickup.requirement.pickup_scene.')

    source_type = fields.Selection([
       ('iff', 'From IFF (wd_iffm)'),
       ('manual', 'Manual Entry'),
    ], string='Source', default='manual', required=True)

    transport_type_id = fields.Many2one('tlmp.transport.type',
       string='Transport Type', required=True,
       default=lambda self: self.env['tlmp.transport.type']._get_by_code('port_to_warehouse').id)

    # ---- Cargo type control ----
    cargo_type = fields.Selection([
       ('container', 'Container'),
       ('pallet', 'Pallet'),
       ('piece', 'Piece / Bulk'),
    ], string='Cargo Type', default='container', required=True)
    business_driver = fields.Selection([
       ('plan_driven', 'B1 Plan-Driven'),
       ('commercial', 'B2 Commercial'),
    ], string='Business Driver', default='plan_driven', required=True,
       help='Business matrix dimension B.')
    cargo_category = fields.Selection([
       ('container', 'C1 Container'),
       ('pallet', 'C2 Pallet'),
       ('piece', 'C3 Piece'),
    ], string='Cargo Category', compute='_compute_cargo_category', store=True,
       help='Business matrix dimension C; root determines the Cargo Category.')
    carrier_type = fields.Selection([
       ('own_fleet', 'D1 Own Fleet'),
       ('truck', 'D2 Third-Party Truck'),
       ('courier', 'D3 Courier'),
    ], string='Carrier Type', default='truck', required=True,
       help='Business matrix dimension D.')
    t1_attribute = fields.Selection([
       ('t1', 'E1 T1'),
       ('normal', 'E2 Normal'),
    ], string='T1 Attribute', default='normal', required=True,
       help='Business matrix dimension E.')
    dg_attribute = fields.Selection([
       ('dg', 'F1 Dangerous'),
       ('normal', 'F2 Normal'),
    ], string='DG Attribute', default='normal', required=True,
       help='Business matrix dimension F.')
    matrix_code = fields.Char(
       string='Matrix Code', compute='_compute_matrix_code', store=True,
       help='Six-dimension combination code, e.g. S1-B1-C1-D2-E2-F2.')
    matrix_version = fields.Char(
       string='Matrix Version', default='V1.0', readonly=True, copy=False)
    matrix_snapshot_status = fields.Selection([
       ('draft', 'Draft'),
       ('frozen', 'Frozen'),
    ], string='Matrix Snapshot Status', default='draft', readonly=True, copy=False)
    matrix_validation_result = fields.Selection([
       ('pass', 'PASS'),
       ('warning', 'WARNING'),
       ('block', 'BLOCK'),
    ], string='Matrix Validation', compute='_compute_matrix_validation', store=True)
    matrix_validation_violations = fields.Text(
       string='Matrix Violations', compute='_compute_matrix_validation', store=True)

    # ---- Cargo fields (pallet goes to pickup.plan, container mgmt at pickup.plan level) ----
    cargo_line_ids = fields.One2many("tlmp.transport.cargo.line", "request_id", string="Cargo Lines")
    pallet_count = fields.Integer(string="Pallets")
    package_count = fields.Integer(string='Packages')
    cargo_weight = fields.Float(string='Weight (kg)', digits='Stock Weight')
    cargo_volume = fields.Float(string='Volume (m3)', digits='Volume')
    cargo_description = fields.Text(string='Cargo Description')

    # ---- Partner ----
    partner_id = fields.Many2one('res.partner', string='Customer',
                                domain=[('is_company', '=', True)],
                                help='Cargo owner / entrusting customer. Optional when the destination is entered manually as a free address.')
    customer_ref = fields.Char(string='Customer Reference')
    contact_person = fields.Char(string='Contact Person')
    contact_phone = fields.Char(string='Contact Phone')
    contact_email = fields.Char(string='Contact Email')

    # ---- Destination / Scene fields ----
    terminal_id = fields.Many2one('res.partner', string='Origin Terminal / Port',
                                 domain=[('is_company', '=', True)])
    warehouse_id = fields.Many2one('stock.warehouse', string='Destination Warehouse')
    source_warehouse_id = fields.Many2one('stock.warehouse', string='Source Warehouse')
    delivery_address = fields.Text(string='Delivery Address')
    delivery_contact = fields.Char(string='Delivery Contact')
    delivery_phone = fields.Char(string='Delivery Phone')

    # Sprint44: structured origin address fields
    origin_street = fields.Char(string='Origin Street')
    origin_zip = fields.Char(string='Origin Zip')
    origin_city = fields.Char(string='Origin City')
    origin_state_id = fields.Many2one('res.country.state', string='Origin State')
    origin_country_id = fields.Many2one('res.country', string='Origin Country')
    # Sprint44: structured destination address fields
    destination_street = fields.Char(string='Destination Street')
    destination_zip = fields.Char(string='Destination Zip')
    destination_city = fields.Char(string='Destination City')
    destination_state_id = fields.Many2one('res.country.state', string='Destination State')
    destination_country_id = fields.Many2one('res.country', string='Destination Country')
    pickup_location_id = fields.Many2one('res.partner', string='Pickup Location')
    delivery_location_id = fields.Many2one('res.partner', string='Delivery Location')

    # ---- Scheduling fields ----
    carrier_id = fields.Many2one('res.partner', string='Trucking Company',
                                domain=[('is_carrier', '=', True)])
    planned_pickup_date = fields.Datetime(string='Planned Pickup')
    driver_name = fields.Char(string='Driver Name')
    driver_phone = fields.Char(string='Driver Phone')
    vehicle_plate = fields.Char(string='Vehicle Plate')

    # ---- Dates ----
    requested_pickup_date = fields.Datetime(string='Requested Pickup')
    requested_delivery_date = fields.Datetime(string='Requested Delivery')

    # ---- Downstream document links ----
    pickup_plan_ids = fields.One2many('pickup.plan', 'transport_request_id',
                                      string='Pickup Plans', copy=False)
    inquiry_ids = fields.One2many('tlmp.transport.inquiry', 'request_id',
                                  string='Inquiries', copy=False)
    quote_ids = fields.One2many('tlmp.transport.quote', 'request_id',
                                string='Quotes', copy=False)
    has_accepted_quote = fields.Boolean(
        string='Has Accepted Quote', compute='_compute_has_accepted_quote', store=True,
        help='Whether the commercial flow already has an accepted quote.')

    @api.depends('quote_ids.state')
    def _compute_has_accepted_quote(self):
        for r in self:
            r.has_accepted_quote = any(q.state == 'accepted' for q in r.quote_ids)

    # ---- Misc ----
    special_requirements = fields.Text(string='Special Requirements')
    has_dangerous_goods = fields.Boolean(string='Dangerous Goods', default=False)
    customs_declaration_ref = fields.Char(string='Customs Decl. Ref.')
    wms_transfer_order_ref = fields.Char(string='WMS Transfer Ref.')

    # ---- Status ----
    state = fields.Selection([
       ('draft', 'Draft'),
       ('confirmed', 'Confirmed'),
       ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    # -----------------------------------------------------------
    # Sequence
    # -----------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
       for vals in vals_list:
           if vals.get('name', _('New')) == _('New'):
               vals['name'] = self.env['ir.sequence'].next_by_code('tlmp.request.seq') or _('New')
           if not vals.get('business_driver') and vals.get('request_type'):
               vals['business_driver'] = vals['request_type']
           if not vals.get('dg_attribute') and vals.get('has_dangerous_goods'):
               vals['dg_attribute'] = 'dg' if vals.get('has_dangerous_goods') else 'normal'
           self._raise_if_matrix_block_vals(vals)
       return super().create(vals_list)

    def write(self, vals):
        for r in self:
            self._raise_if_matrix_block_vals(vals, record=r)
        return super().write(vals)

    def _raise_if_matrix_block_vals(self, vals, record=None):
        ctx = self._matrix_vals_context(vals, record)
        res = BusinessMatrixEngine.validate(self.env, ctx)
        if res['result'] == 'block':
            msgs = '; '.join(v.get('message', '') for v in res['violations'])
            raise UserError(_('Business Matrix BLOCK: %s') % msgs)

    def _matrix_vals_context(self, vals, record=None):
        scene_id = vals.get('scene_id', record.scene_id.id if record else False)
        carrier_id = vals.get('carrier_id', record.carrier_id.id if record else False)
        capabilities = set()
        if carrier_id:
            capabilities = set(
                self.env['res.partner'].browse(carrier_id)
                .carrier_capability_ids.mapped('code'))
        categories = set()
        if record:
            categories = set(record.cargo_line_ids.mapped('cargo_category'))
        scene = self.env['tlmp.transport.scene'].browse(scene_id) if scene_id else False
        cargo_category = (
            vals.get('cargo_category') or vals.get('cargo_type')
            or (record.cargo_category if record else False)
            or (record.cargo_type if record else False))
        return {
            'scene_code': scene.code if scene else (
                record.scene_id.code if record and record.scene_id else False),
            'business_driver': vals.get(
                'business_driver', record.business_driver if record else 'plan_driven'),
            'cargo_category': cargo_category or 'piece',
            'carrier_type': vals.get(
                'carrier_type', record.carrier_type if record else 'truck'),
            't1_attribute': vals.get(
                't1_attribute', record.t1_attribute if record else 'normal'),
            'dg_attribute': vals.get(
                'dg_attribute', record.dg_attribute if record else 'normal'),
            'carrier_capabilities': capabilities,
            'mixed_roots': len(categories) > 1,
        }

    @api.depends('cargo_type')
    def _compute_cargo_category(self):
        for r in self:
            r.cargo_category = r.cargo_type or 'piece'

    @api.depends('scene_id.code', 'business_driver', 'cargo_category',
                 'carrier_type', 't1_attribute', 'dg_attribute')
    def _compute_matrix_code(self):
        for r in self:
            r.matrix_code = '-'.join([
                SCENE_S_CODES.get(r.scene_id.code, 'S0') if r.scene_id else 'S0',
                BUSINESS_DRIVER.get(r.business_driver, 'B0'),
                CARGO_CATEGORY.get(r.cargo_category, 'C0'),
                CARRIER_TYPE.get(r.carrier_type, 'D0'),
                T1_ATTRIBUTE.get(r.t1_attribute, 'E0'),
                DG_ATTRIBUTE.get(r.dg_attribute, 'F0'),
            ])

    def _matrix_context(self):
        capabilities = set()
        if self.carrier_id:
            capabilities = set(self.carrier_id.carrier_capability_ids.mapped('code'))
        categories = set(self.cargo_line_ids.mapped('cargo_category'))
        return {
            'scene_code': self.scene_id.code if self.scene_id else False,
            'business_driver': self.business_driver,
            'cargo_category': self.cargo_category,
            'carrier_type': self.carrier_type,
            't1_attribute': self.t1_attribute,
            'dg_attribute': self.dg_attribute,
            'carrier_capabilities': capabilities,
            'mixed_roots': len(categories) > 1,
        }

    @api.depends('scene_id.code', 'business_driver', 'cargo_category',
                 'carrier_type', 't1_attribute', 'dg_attribute',
                 'carrier_id.carrier_capability_ids',
                 'cargo_line_ids.cargo_category')
    def _compute_matrix_validation(self):
        for r in self:
            res = BusinessMatrixEngine.validate(self.env, r._matrix_context())
            r.matrix_validation_result = res['result']
            r.matrix_validation_violations = json.dumps(
                res['violations'], ensure_ascii=False)


    # -----------------------------------------------------------
    # State transitions
    # -----------------------------------------------------------
    def action_confirm(self):
        self.write({'state': 'confirmed', 'matrix_snapshot_status': 'frozen'})
        return True

    def action_cancel(self):
       self.write({'state': 'cancelled'})
       return True

    # -----------------------------------------------------------
    # Plan-Driven flow: Schedule
    # -----------------------------------------------------------
    def action_go_schedule(self):
       self.ensure_one()
       if self.request_type != 'plan_driven':
           raise UserError(_('Schedule is only available for plan-driven requests.'))
       # Reuse existing Pickup Plan if already created
       # Reuse existing Pickup Plan (search by request_id or name)
       plan_name = self.name.replace('REQ', 'PUP-')
       existing_plan = self.env['pickup.plan'].search([
           '|',
           ('transport_request_id', '=', self.id),
           ('name', '=', plan_name),
       ], limit=1)
       
       if existing_plan:
           plan = existing_plan
           # Update transport_request_id if not set (first-time fix)
           if not plan.transport_request_id:
               plan.transport_request_id = self.id
       else:
           # Create a new Pickup Plan
           plan = self.env['pickup.plan'].create({
               'name': plan_name,
               'transport_request_id': self.id,
               'scene_id': self.scene_id.id,
               'cargo_type': self.cargo_type,
               'destination_type': self.destination_type,
               'terminal_id': self.terminal_id.id,
               'warehouse_id': self.warehouse_id.id,
               'source_type': 'manual',
               # Sprint45: copy address snapshot from request
               'origin_street': self.origin_street,
               'origin_zip': self.origin_zip,
               'origin_city': self.origin_city,
               'origin_state_id': self.origin_state_id.id if self.origin_state_id else False,
               'origin_country_id': self.origin_country_id.id if self.origin_country_id else False,
               'destination_street': self.destination_street,
               'destination_zip': self.destination_zip,
               'destination_city': self.destination_city,
               'destination_state_id': self.destination_state_id.id if self.destination_state_id else False,
               'destination_country_id': self.destination_country_id.id if self.destination_country_id else False,
           })
           # Copy cargo lines to pickup plan container lines
           for cl in self.cargo_line_ids:
               self.env['pickup.plan.container.line'].create({
                   'plan_id': plan.id,
                   'container_number': cl.container_no or '',
                   'container_type': cl.container_type or '20GP',
                   'bl_number': cl.bl_number or '',
                   'weight': cl.gross_weight,
               })
       
       return {
           'type': 'ir.actions.client',
           'tag': 'tlmp_schedule.action',
           'target': 'self',
       }

    # -----------------------------------------------------------
    # Plan-Driven flow: Create Transport Order
    # -----------------------------------------------------------
    def action_create_transport_order(self):
       self.ensure_one()
       if self.request_type != 'plan_driven':
           raise UserError(_('Direct order creation is for plan-driven requests only.'))
       type_map = {
           'warehouse': 'port_to_warehouse',
           'warehouse_transfer': 'warehouse_transfer',
           'customer': 'to_customer', 'self_pickup': 'to_customer',
       }
       tr_type = type_map.get(self.destination_type, 'port_to_warehouse')
       order = self.env['tlmp.transport.order'].create({
           'transport_type_id': self.env['tlmp.transport.type']._get_by_code(tr_type).id,
           'fleet_operation_mode': 'subcontracted',
           'partner_id': self.partner_id.id or self.env.user.partner_id.id,
           'carrier_id': self.carrier_id.id if self.carrier_id else False,
           'cargo_description': self.cargo_description or _('Request %s') % self.name,
           'cargo_weight': self.cargo_weight, 'cargo_volume': self.cargo_volume,
           'pallet_count': self.pallet_count, 'package_count': self.package_count,
           'planned_pickup_date': self.planned_pickup_date or self.requested_pickup_date,
           'driver_name': self.driver_name, 'driver_phone': self.driver_phone,
           'vehicle_plate': self.vehicle_plate, 'notes': self.special_requirements,
       })
       return {
           'type': 'ir.actions.act_window',
           'res_model': 'tlmp.transport.order', 'view_mode': 'form',
           'res_id': order.id, 'target': 'current',
       }

    # -----------------------------------------------------------
    # Commercial flow: Start Inquiry
    # -----------------------------------------------------------
    def action_start_inquiry(self):
       self.ensure_one()
       if self.request_type != 'commercial':
           raise UserError(_('Inquiry is only available for commercial requests.'))
       if self.has_accepted_quote:
           raise UserError(_('This request already has an accepted quote. Start a new inquiry only after the quote is rejected or cancelled.'))
       cargo_summary = self.cargo_description
       cargo_lines = self.cargo_line_ids
       if not cargo_summary and cargo_lines:
           cargo_summary = '\n'.join(
               ' - '.join(x for x in (cl.description, cl.container_no, cl.bl_number) if x)
               for cl in cargo_lines)
       if not cargo_summary and self.cargo_type == 'pallet':
           cargo_summary = _('Pallet %s / Package %s') % (
               self.pallet_count or 0, self.package_count or 0)
       if not cargo_lines and self.cargo_type == 'pallet':
           inquiry_lines = [(0, 0, {
               'description': cargo_summary,
               'quantity': self.pallet_count or 1.0,
           })]
       elif not cargo_lines and self.cargo_type == 'piece':
           inquiry_lines = [(0, 0, {
               'description': _('Pieces %s') % (self.package_count or 0),
               'quantity': self.package_count or 1.0,
           })]
       else:
           inquiry_lines = [(0, 0, {
               'description': cl.description or cl.container_no or cl.bl_number or _('Cargo'),
               'quantity': 1.0,
           }) for cl in cargo_lines]
       inquiry = self.env['tlmp.transport.inquiry'].create({
           'request_id': self.id,
           'partner_id': self.carrier_id.id if self.carrier_id else False,
           'cargo_summary': cargo_summary or '',
           'weight_kg': self.cargo_weight or sum(cl.gross_weight for cl in cargo_lines),
           'volume_m3': self.cargo_volume or sum(cl.volume_m3 for cl in cargo_lines),
           'pickup_date': self.requested_pickup_date,
           'line_ids': inquiry_lines,
       })
       return {
           'type': 'ir.actions.act_window',
           'res_model': 'tlmp.transport.inquiry', 'view_mode': 'form',
           'res_id': inquiry.id, 'target': 'current',
       }

    # -----------------------------------------------------------

    # -----------------------------------------------------------
    # Commercial flow: Create Orders from Accepted Quotes
    # -----------------------------------------------------------
    def action_create_orders_from_quotes(self):
       self.ensure_one()
       if self.request_type != 'commercial':
          raise UserError(_('This action is only available for commercial requests.'))
       accepted = self.quote_ids.filtered(lambda q: q.state == 'accepted')
       if not accepted:
          raise UserError(_('No accepted quotes found.'))
       existing_ids = accepted.mapped('transport_order_id').ids
       created = []
       for quote in accepted:
          if not quote.transport_order_id:
              order = quote._auto_create_order()
              created.append(order.id)
       target_ids = existing_ids + created
       if target_ids:
          if len(target_ids) == 1:
              return {'type': 'ir.actions.act_window', 'res_model': 'tlmp.transport.order',
                      'view_mode': 'form', 'res_id': target_ids[0], 'target': 'current'}
          return {'type': 'ir.actions.act_window', 'res_model': 'tlmp.transport.order',
                  'view_mode': 'list', 'domain': [('id', 'in', target_ids)], 'target': 'current'}
       return {'type': 'ir.actions.act_window', 'res_model': 'tlmp.transport.request', 'view_mode': 'form', 'res_id': self.id}


    # Constraints
    # -----------------------------------------------------------
    @api.onchange('scene_id')
    def _onchange_scene_id(self):
        for rec in self:
            if not rec.scene_id:
                continue
            scene = rec.scene_id
            rec.destination_type = 'warehouse_transfer' if scene.code == 'warehouse_transfer' else scene.destination_type
            rec.request_type = 'plan_driven' if scene.scene_type in ('plan_driven', 'mixed') else 'commercial'
            rec.business_driver = rec.request_type
            if scene.destination_type == 'customer':
                rec.warehouse_id = False
            else:
                rec.partner_id = False

    @api.onchange('terminal_id')
    def _onchange_terminal_id(self):
        for r in self:
            if r.terminal_id and not r.origin_street:
                r.origin_street = r.terminal_id.street
                r.origin_zip = r.terminal_id.zip
                r.origin_city = r.terminal_id.city
                r.origin_state_id = r.terminal_id.state_id
                r.origin_country_id = r.terminal_id.country_id

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        for r in self:
            if r.carrier_id:
                partner_type = r.carrier_id.carrier_type
                r.carrier_type = {
                    'own_fleet': 'own_fleet',
                    'contracted': 'truck',
                    'subcontracted': 'truck',
                }.get(partner_type, 'truck')

    @api.onchange('source_warehouse_id')
    def _onchange_source_warehouse_id(self):
        for r in self:
            wh = r.source_warehouse_id
            if wh and wh.partner_id and not r.origin_street:
                r.origin_street = wh.partner_id.street
                r.origin_zip = wh.partner_id.zip
                r.origin_city = wh.partner_id.city
                r.origin_state_id = wh.partner_id.state_id
                r.origin_country_id = wh.partner_id.country_id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for r in self:
            if r.partner_id and not r.destination_street and r.scene_id and r.scene_id.destination_type == 'customer':
                r.destination_street = r.partner_id.street
                r.destination_zip = r.partner_id.zip
                r.destination_city = r.partner_id.city
                r.destination_state_id = r.partner_id.state_id
                r.destination_country_id = r.partner_id.country_id

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        for r in self:
            if r.warehouse_id and not r.destination_street:
                wh = r.warehouse_id
                if wh.partner_id:
                    r.destination_street = wh.partner_id.street
                    r.destination_zip = wh.partner_id.zip
                    r.destination_city = wh.partner_id.city
                    r.destination_state_id = wh.partner_id.state_id
                    r.destination_country_id = wh.partner_id.country_id

    @api.onchange('cargo_line_ids')
    def _onchange_cargo_line_totals(self):
        for r in self:
            pallet_count, package_count, weight, volume = r._get_cargo_totals(
                update_lines=True)
            r.pallet_count = pallet_count
            r.package_count = package_count
            r.cargo_weight = weight
            r.cargo_volume = volume

    def _get_cargo_totals(self, update_lines=False):
        """Roll up cargo node totals for the request header."""
        pallet_count = 0
        package_count = 0
        weight = 0.0
        volume = 0.0
        for line in self.cargo_line_ids:
            level = line.packaging_level or 'piece'
            line_weight = 0.0
            line_volume = 0.0
            if level == 'handling_unit':
                line_packages = int(round(
                    (line.qty or 0.0) * (line.pieces_per_pallet or 0)))
                line_weight = (
                    (line.qty or 0.0) * (line.pallet_gross_weight_kg or 0.0))
                line_volume = (
                    (line.qty or 0.0) * (line.pallet_volume_m3 or 0.0))
                pallet_count += line.qty or 0.0
                package_count += line_packages
            elif level in ('package', 'piece'):
                line_packages = int(round(line.qty or 0.0))
                line_weight = (
                    (line.qty or 0.0) * (line.piece_gross_weight_kg or 0.0))
                line_volume = (
                    (line.qty or 0.0) * (line.piece_volume_m3 or 0.0))
                package_count += line.qty or 0.0
            else:  # container leaf: manual equipment totals
                line_packages = 0
                line_weight = line.gross_weight or 0.0
                line_volume = line.volume_m3 or 0.0
            if update_lines:
                line.packages = line_packages
                line.gross_weight = line_weight
                line.volume_m3 = line_volume
            if line.child_cargo_line_ids:
                continue
            weight += line_weight
            volume += line_volume
        return int(round(pallet_count)), int(round(package_count)), weight, volume

    @api.constrains('scene_id', 'destination_type', 'warehouse_id', 'source_warehouse_id', 'partner_id', 'destination_street')
    def _check_destination_fields(self):
       for rec in self:
           scene = rec.scene_id
           dest = scene.destination_type if scene else rec.destination_type
           if dest == 'warehouse' or (not scene and rec.destination_type == 'warehouse_transfer'):
               if not rec.warehouse_id:
                   raise UserError(_('Destination Warehouse required for warehouse/transfer.'))
           if (scene and scene.code == 'warehouse_transfer') or (not scene and rec.destination_type == 'warehouse_transfer'):
               if not rec.source_warehouse_id:
                   raise UserError(_('Source Warehouse required for warehouse transfer.'))
           if dest in ('customer', 'self_pickup') and not rec.partner_id and not rec.destination_street:
               raise UserError(_('Customer or Destination Address required for delivery/self-pickup.'))

    # -----------------------------------------------------------
    # IFFM reference (read-only soft link)
    # -----------------------------------------------------------
    @api.model
    def _get_reference_models(self):
       models = []
       if self.env.get('import.pickup.requirement'):
           models.append(('import.pickup.requirement', 'Import Pickup Requirement'))
       return models

    iff_requirement_ref = fields.Reference(
       selection=lambda self: self._get_reference_models(),
       string='IFF Pickup Requirement',
       help='Read-only reference to import.pickup.requirement (wd_iffm). No hard dependency.')

    # ---- Onchange: auto-fill from IFFM reference ----
    @api.onchange('iff_requirement_ref')
    def _onchange_iff_requirement_ref(self):
       if not self.iff_requirement_ref:
           return
       req = self.iff_requirement_ref
       if req._name != 'import.pickup.requirement':
           return
       self.source_type = 'iff'
       self.terminal_id = req.terminal_a if hasattr(req, 'terminal_a') else False
       if req.pickup_scene == 'to_our_warehouse' and req.warehouse_id:
           self.destination_type = 'warehouse'
           self.warehouse_id = req.warehouse_id
       elif req.pickup_scene == 'to_customer_address':
           self.destination_type = 'customer'
           self.delivery_address = (req.delivery_street or '') + ', ' + (req.delivery_zip or '') + ' ' + (req.delivery_city or '')
           self.delivery_contact = req.delivery_contact_id.display_name if req.delivery_contact_id else ''
           self.delivery_phone = req.delivery_phone or ''
       elif req.pickup_scene == 'customer_self_pickup':
           self.destination_type = 'self_pickup'
           self.delivery_contact = req.self_pickup_contact_id.display_name if req.self_pickup_contact_id else ''
           self.delivery_phone = req.self_pickup_phone or ''
       self.request_type = 'plan_driven' if self.destination_type in ('warehouse', 'warehouse_transfer') else 'commercial'
