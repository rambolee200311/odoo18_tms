from odoo.tests.common import TransactionCase

class TestSettlementBatch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Batch = self.env['tlmp.carrier.settlement.batch']
        self.partner = self.env['res.partner'].create({'name': 'Carrier', 'is_company': True})

    def test_01_create_batch(self):
        b = self.Batch.create({
            'carrier_partner_id': self.partner.id,
            'period_start': '2026-01-01',
            'period_end': '2026-01-31',
        })
        self.assertTrue(b.id)
        self.assertEqual(b.state, 'draft')

    def test_02_batch_state_machine(self):
        b = self.Batch.create({
            'carrier_partner_id': self.partner.id,
            'period_start': '2026-02-01',
            'period_end': '2026-02-28',
        })
        b.action_confirm()
        self.assertEqual(b.state, 'confirmed')
        b.action_close()
        self.assertEqual(b.state, 'closed')
