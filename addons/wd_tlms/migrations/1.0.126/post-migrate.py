# -*- coding: utf-8 -*-
"""Sprint52-Fix3: inquiry/quote state convergence and traceability backfill."""

from odoo import SUPERUSER_ID, api, fields


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Inquiry = env['tlmp.transport.inquiry'].sudo()
    Quote = env['tlmp.transport.quote'].sudo().with_context(
        skip_quote_source_inquiry_check=True)
    Order = env['tlmp.transport.order'].sudo()

    accepted_code = env['tlmp.transport.event.code'].sudo().search([
        ('code', '=', 'INQUIRY_ACCEPTED'),
    ], limit=1)
    if accepted_code and not accepted_code.deprecated_at:
        accepted_code.write({'deprecated_at': fields.Datetime.now()})

    for inquiry in Inquiry.search([('state', '=', 'accepted')]):
        inquiry.write({
            'state': 'selected',
            'selected_carrier_id': (
                inquiry.partner_id.id or inquiry.selected_carrier_id.id),
        })

    for quote in Quote.search([('state', 'in', ('sent', 'issued'))]):
        quote.write({'state': 'draft', 'communication_status': 'sent'})
    for quote in Quote.search([('state', 'in', ('approved', 'confirmed'))]):
        quote.write({
            'state': 'accepted',
            'customer_accept': True,
            'confirmation_source': 'customer',
        })

    cr.execute(
        """
        SELECT q.id, l.create_date, l.create_uid
        FROM tlmp_transport_quote q
        JOIN tlmp_transport_event_ledger l
          ON l.res_model = 'tlmp.transport.quote'
         AND l.res_id = q.id
         AND l.event_type IN ('QUOTE_ACCEPTED', 'QUOTE_CONFIRMED')
        WHERE q.state = 'accepted'
        """)
    for quote_id, accepted_date, uid in cr.fetchall():
        vals = {}
        if accepted_date:
            vals['accepted_date'] = accepted_date
        if uid:
            vals['accepted_by'] = uid
        if vals:
            Quote.browse(quote_id).write(vals)

    for quote in Quote.search([('state', '=', 'accepted')]):
        vals = {}
        if not quote.accepted_date and quote.create_date:
            vals['accepted_date'] = quote.create_date
        if not quote.accepted_by and quote.create_uid:
            vals['accepted_by'] = quote.create_uid.id
        if vals:
            quote.write(vals)

    for order in Order.search([('quote_id', '!=', False)]):
        quote = order.quote_id
        vals = {}
        if not order.inquiry_id and quote.inquiry_id:
            vals['inquiry_id'] = quote.inquiry_id.id
        if not order.carrier_id and quote.inquiry_id and quote.inquiry_id.partner_id:
            vals['carrier_id'] = quote.inquiry_id.partner_id.id
        if vals:
            order.write(vals)
        if quote and not quote.transport_order_id:
            quote.write({'transport_order_id': order.id})
        inquiry = order.inquiry_id or quote.inquiry_id
        if inquiry and not inquiry.selected_quote_id:
            inquiry.write({'selected_quote_id': quote.id})
