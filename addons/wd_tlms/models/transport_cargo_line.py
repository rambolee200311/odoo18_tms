# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportCargoLine(models.Model):
    _name = 'tlmp.transport.cargo.line'
    _description = 'Transport Cargo Line (Snapshot)'
    _order = 'sequence, id'

    request_id = fields.Many2one('tlmp.transport.request', string='Transport Request',
                                 index=True, ondelete='cascade')
    order_id = fields.Many2one('tlmp.transport.order', string='Transport Order',
                               index=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Char(string='Description', required=True)
    commodity = fields.Char(string='Commodity')
    qty = fields.Float(string='Quantity (Units)', default=1.0,
        help='Number of units in this line, e.g. 10 pallets. '
             'The request header totals are the sum of all lines.')
    uom = fields.Char(string='UoM',
        help='Unit of Measure for Quantity, e.g. pallet, carton, piece.')
    packages = fields.Integer(string='Packages',
        help='Inner packages/parcels of this line (total for the line).')
    gross_weight = fields.Float(string='Gross Weight (kg)',
        help='Gross weight of this line (total, not per unit).')
    net_weight = fields.Float(string='Net Weight (kg)',
        help='Net weight of this line (total, not per unit).')
    volume_m3 = fields.Float(string='Volume (m3)',
        help='Volume of this line (total, not per unit).')
    container_no = fields.Char(string='Container No.',
                               help='Transport document snapshot only — does not replace container tracking master data')

    bl_number = fields.Char(string='BL Number',
                            help='Bill of Lading number for this container')
    container_type = fields.Char(string='Container Type', default='20GP',
                                 help='ISO container type code, e.g. 20GP, 40HC')
    source_type = fields.Selection([
        ('manual', 'Manual Entry'),
        ('outbound_order', 'Outbound Reference'),
        ('system', 'System/API'),
    ], string='Source Type', required=True, default='manual')
    outbound_ref_id = fields.Many2one('ir.model', string='Outbound Document Ref.',
                                      help='Reference to source outbound document (model not hardcoded)')
    has_dangerous_goods = fields.Boolean(string='Has Dangerous Goods')
    dangerous_goods_profile_id = fields.Many2one(
        'tlmp.transport.dangerous.goods.profile',
        string='Dangerous Goods Profile',
        help='ADR attribute template linked to UN dictionary. '
             'NOT an ADR field expansion on cargo_line.')
    notes = fields.Text(string='Notes')

    @api.constrains('request_id', 'order_id')
    def _check_owner_exclusive(self):
        for r in self:
            if r.request_id and r.order_id:
                raise ValidationError(_('Cargo line cannot belong to both request and order.'))

    def copy_to_order(self, order):
        """Copy this cargo line to an order, creating an independent record."""
        self.ensure_one()
        new = self.copy(default={'request_id': False, 'order_id': order.id})
        return new


class TransportSceneCargoRule(models.Model):
    _name = 'tlmp.transport.scene.cargo.rule'
    _description = 'Scene Cargo Rule'
    _rec_name = 'scene_id'

    scene_id = fields.Many2one('tlmp.transport.scene', string='Scene',
                               required=True, ondelete='cascade')
    allowed_source_type = fields.Selection([
        ('manual', 'Manual Only'),
        ('outbound_order', 'Outbound Only'),
        ('both', 'Manual + Outbound'),
        ('none', 'No Cargo'),
    ], string='Allowed Source', required=True, default='manual')
    container_required = fields.Boolean(string='Container Required', default=False)
    cargo_required = fields.Boolean(string='Cargo Required', default=True)
    priority = fields.Integer(string='Priority', default=10)
    condition_domain = fields.Char(string='Condition Domain',
                                   help='Reserved for future use. Not evaluated in Sprint22.')
    active = fields.Boolean(string='Active', default=True)
