# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TransportRequest(models.Model):
   _name = 'tlmp.transport.request'
   _description = 'Transport Request (Unified Entry Point)'
   _inherit = ['mail.thread', 'mail.activity.mixin']
   _order = 'create_date desc, id desc'
   _rec_name = 'name'

   # ---- Identity ----
   name = fields.Char(string='Request No.', required=True, copy=False,
                      default=lambda self: _('New'))

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

   # ---- Existing transport_type kept for backward compat ----
   transport_type = fields.Selection([
       ('port_to_warehouse', 'Port to Warehouse'),
       ('to_customer', 'To Customer'),
       ('pickup_to_warehouse', 'Pickup to Warehouse'),
       ('warehouse_transfer', 'Warehouse Transfer'),
       ('reverse_logistics', 'Reverse Logistics'),
   ], string='Transport Type', required=True, default='port_to_warehouse')

   # ---- Cargo type control ----
   cargo_type = fields.Selection([
       ('container', 'Container'),
       ('pallet', 'Pallet / Piece'),
   ], string='Cargo Type', default='container', required=True)

   # ---- Cargo fields (pallet goes to pickup.plan, container mgmt at pickup.plan level) ----
   pallet_count = fields.Integer(string='Pallets')
   package_count = fields.Integer(string='Packages')
   cargo_weight = fields.Float(string='Weight (kg)', digits='Stock Weight')
   cargo_volume = fields.Float(string='Volume (m3)', digits='Volume')
   cargo_description = fields.Text(string='Cargo Description')

   # ---- Partner ----
   partner_id = fields.Many2one('res.partner', string='Customer',
                                domain=[('is_company', '=', True)])
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
       return {
           'type': 'ir.actions.act_url',
           'url': '/pickup_schedule',
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
           'transport_type': tr_type,
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
       inquiry = self.env['tlmp.transport.inquiry'].create({
           'request_id': self.id,
           'partner_id': self.carrier_id.id or self.env.user.partner_id.id,
           'cargo_summary': self.cargo_description or '',
           'weight_kg': self.cargo_weight, 'volume_m3': self.cargo_volume,
           'pickup_date': self.requested_pickup_date,
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
       created = []
       for quote in accepted:
          if hasattr(quote, '_auto_create_order') and not quote.transport_order_id:
              order = quote._auto_create_order()
              created.append(order.id)
       if created:
          return {'type': 'ir.actions.act_window', 'res_model': 'tlmp.transport.order', 'view_mode': 'list', 'domain': [('id', 'in', created)], 'target': 'current'}
       return {'type': 'ir.actions.act_window', 'res_model': 'tlmp.transport.request', 'view_mode': 'form', 'res_id': self.id}


   # Constraints
   # -----------------------------------------------------------
   @api.constrains('destination_type', 'warehouse_id', 'source_warehouse_id', 'partner_id')
   def _check_destination_fields(self):
       for rec in self:
           if rec.destination_type in ('warehouse', 'warehouse_transfer') and not rec.warehouse_id:
               raise UserError(_('Destination Warehouse required for warehouse/transfer.'))
           if rec.destination_type == 'warehouse_transfer' and not rec.source_warehouse_id:
               raise UserError(_('Source Warehouse required for warehouse transfer.'))
           if rec.destination_type in ('customer', 'self_pickup') and not rec.partner_id:
               raise UserError(_('Customer required for delivery/self-pickup.'))

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
