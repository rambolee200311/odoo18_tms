from odoo import models, fields, api, _


class TransportTracking(models.Model):
    _name = 'tlmp.transport.tracking'
    _description = 'Tracking Event'
    _order = 'timestamp desc, id desc'

    order_id = fields.Many2one('tlmp.transport.order', string='Order', required=True)
    event_code = fields.Selection([
        ('assigned', 'Assigned'), ('pickup', 'Pickup'),
        ('en_route', 'En Route'), ('arrival', 'Arrival'),
        ('unloading', 'Unloading'), ('delivered', 'Delivered'),
        ('exception', 'Exception'),
        ('t1_declared', 'T1 Declared'), ('t1_sealed', 'T1 Sealed'),
        ('t1_in_transit', 'T1 In Transit'), ('t1_arrived', 'T1 Arrived'),
        ('t1_closed', 'T1 Closed'),
    ], string='Event', required=True)
    event_name = fields.Char(string='Event Name')
    timestamp = fields.Datetime(string='Timestamp', required=True, default=fields.Datetime.now)
    location_text = fields.Char(string='Location')
    latitude = fields.Float(string='Latitude', digits=(9, 6))
    longitude = fields.Float(string='Longitude', digits=(9, 6))
    driver_notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Photos')
    created_by = fields.Selection([
        ('system', 'System'), ('driver', 'Driver'), ('operator', 'Operator'),
    ], string='Created By', default='operator')

    @api.model
    def create_event(self, order_id, event_code, vals=None):
        vals = vals or {}
        vals.update({'order_id': order_id, 'event_code': event_code})
        return self.create(vals)
