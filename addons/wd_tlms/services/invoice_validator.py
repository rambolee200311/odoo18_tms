import json
from odoo import api, fields, models, _

class InvoiceValidator(models.AbstractModel):
    _name = 'tlmp.invoice.validator'
    _description = 'Invoice Validator — Idempotency + Schema'

    @api.model
    def check_idempotency(self, carrier_id, external_invoice_no, invoice_version, external_line_key=False):
        domain = [('carrier_id', '=', carrier_id),
                  ('external_invoice_no', '=', external_invoice_no)]
        existing = self.env['tlmp.carrier.billing.document'].search(domain)
        if existing and invoice_version:
            existing = existing.filtered(lambda d: d.invoice_version == invoice_version)
        if existing and not external_line_key:
            return {'duplicate': True, 'existing_document': existing[:1].id}
        if external_line_key and existing:
            line_domain = [('document_id', 'in', existing.ids),
                           ('external_line_key', '=', external_line_key)]
            line_exists = self.env['tlmp.carrier.billing.line'].search(line_domain)
            if line_exists:
                return {'duplicate': True, 'existing_line': line_exists[:1].id}
        return {'duplicate': False}

    @api.model
    def validate_row(self, parsed, template):
        errors = []
        mapping = template.mapping_json
        try:
            mapping = json.loads(mapping)
        except (json.JSONDecodeError, TypeError):
            errors.append(('INVALID_MAPPING', 'Template mapping is not valid JSON'))
        return errors
        
