# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class WorkflowEngine(models.AbstractModel):
    """Shared transition service: guard -> ledger -> state write."""

    _name = 'tlmp.workflow.engine'
    _description = 'TLMS Workflow Engine'

    def write_event(self, record, event_type, event_category='state',
                    from_state=False, to_state=False, payload=None):
        self.env['tlmp.transport.event.ledger'].create({
            'res_model': record._name,
            'res_id': record.id,
            'event_type': event_type,
            'event_category': event_category,
            'from_state': from_state or False,
            'to_state': to_state or False,
            'payload': payload,
        })
        return True

    def transition(self, record, to_state, event_type, event_category='state',
                   guard=None, payload=None, extra_vals=None):
        record.ensure_one()
        if guard:
            guard_error = guard(record)
            if guard_error:
                raise UserError(guard_error)
        from_state = record.state if 'state' in record._fields else False
        self.write_event(
            record, event_type, event_category,
            from_state=from_state, to_state=to_state, payload=payload)
        vals = {'state': to_state}
        if extra_vals:
            vals.update(extra_vals)
        record.write(vals)
        return True
