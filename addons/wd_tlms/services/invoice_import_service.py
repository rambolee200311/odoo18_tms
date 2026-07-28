import json
from odoo import api, fields, models, _

class InvoiceImportService(models.AbstractModel):
    _name = 'tlmp.invoice.import.service'
    _description = 'Invoice Import Main Service'

    @api.model
    def run_import(self, import_batch):
        batch = import_batch
        batch.action_preview()
        Parser = self.env['tlmp.invoice.parser']
        Validator = self.env['tlmp.invoice.validator']
        Writer = self.env['tlmp.invoice.writer']

        template = batch.template_id
        if not template:
            batch.write({'state': 'failed'})
            return {'status': 'error', 'message': 'No template configured'}

        # Parse file
        raw = batch.file_data
        if not raw:
            batch.write({'state': 'failed'})
            return {'status': 'error', 'message': 'No file uploaded'}

        import base64
        try:
            raw_bytes = base64.b64decode(raw)
        except Exception:
            batch.write({'state': 'failed'})
            return {'status': 'error', 'message': 'Invalid file data'}

        enc = template.encoding
        if template.file_type == 'csv':
            rows, detected_enc = Parser.parse_csv(raw_bytes, encoding=enc, delimiter=template.delimiter)
        else:
            rows = Parser.parse_xlsx(raw_bytes)

        # Skip header
        data_rows = rows[1:] if template.has_header and rows else rows

        batch.write({'total_lines': len(data_rows), 'state': 'validated'})

        success = 0
        errors = 0
        batch.action_import()

        for idx, row in enumerate(data_rows):
            # Check idempotency
            idem = Validator.check_idempotency(
                batch.carrier_partner_id.id,
                '', '', '')
            if idem.get('duplicate'):
                continue

            try:
                doc = Writer.write_document(
                    batch.carrier_partner_id.id, '', '', '')
                line = Writer.write_line(
                    doc.id, {'description': str(row), 'amount': 0}, '')
                success += 1
            except Exception as e:
                errors += 1

        batch.write({
            'success_lines': success,
            'error_lines': errors,
            'state': 'completed' if errors == 0 else 'partial_failed',
        })

        return {'status': 'ok', 'success': success, 'errors': errors}
