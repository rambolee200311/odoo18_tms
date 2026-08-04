# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


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
       ('pallet', 'Pallet / Piece'),
    ], string='Cargo Type', default='container', required=True)

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
       return super().create(vals_list)

    # -----------------------------------------------------------
    # State transitions
    # -----------------------------------------------------------
    def action_confirm(self):
       self.write({'state': 'confirmed'})
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
       if not cargo_summary and self.cargo_line_ids:
           cargo_summary = '\n'.join(
               ' - '.join(x for x in (cl.description, cl.container_no, cl.bl_number) if x)
               for cl in self.cargo_line_ids)
       inquiry = self.env['tlmp.transport.inquiry'].create({
           'request_id': self.id,
           'partner_id': self.carrier_id.id if self.carrier_id else False,
           'cargo_summary': cargo_summary or '',
           'weight_kg': self.cargo_weight or sum(cl.gross_weight for cl in self.cargo_line_ids),
           'volume_m3': self.cargo_volume or sum(cl.volume_m3 for cl in self.cargo_line_ids),
           'pickup_date': self.requested_pickup_date,
           'line_ids': [(0, 0, {
               'description': cl.description or cl.container_no or cl.bl_number or _('Cargo'),
               'quantity': 1.0,
           }) for cl in self.cargo_line_ids],
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
