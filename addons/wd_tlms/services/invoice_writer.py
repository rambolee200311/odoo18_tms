import json
from odoo import api, fields, models, _

class InvoiceWriter(models.AbstractModel):
    _name = 'tlmp.invoice.writer'
    _description = 'Invoice Writer — Create billing.document + line'

    @api.model
    def write_document(self, carrier_id, external_invoice_no, invoice_version, external_document_ref, template_id=False):
        doc = self.env['tlmp.carrier.billing.document'].create({
            'carrier_id': carrier_id,
            'external_invoice_no': external_invoice_no,
            'invoice_version': invoice_version,
            'external_document_ref': external_document_ref,
        })
        return doc

    @api.model
    def write_line(self, document_id, parsed, external_line_key):
        line = self.env['tlmp.carrier.billing.line'].create({
            'document_id': document_id,
            'external_line_key': external_line_key,
            'raw_description': parsed.get('description', ''),
            'net_amount': float(parsed.get('amount', 0)),
        })
        return line
