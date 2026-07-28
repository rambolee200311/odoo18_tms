from odoo.tests.common import TransactionCase

class TestSettlementCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Case = self.env['tlmp.carrier.settlement.case']
        self.CaseLine = self.env['tlmp.carrier.settlement.case.line']

    def test_01_create_case(self):
        c = self.Case.create({'case_type': 'unmatched', 'source': 'auto_matching'})
        self.assertTrue(c.id)
        self.assertEqual(c.state, 'open')
        self.assertTrue(c.name.startswith('CASE-'))

    def test_02_state_transition(self):
        c = self.Case.create({'case_type': 'unmatched'})
        c.action_process()
        self.assertEqual(c.state, 'processing')
        c.action_resolve()
        self.assertEqual(c.state, 'resolved')
        c.action_close()
        self.assertEqual(c.state, 'closed')

    def test_03_cancel_case(self):
        c = self.Case.create({'case_type': 'amount_discrepancy'})
        c.action_cancel()
        self.assertEqual(c.state, 'cancelled')

    def test_04_reopen_case(self):
        c = self.Case.create({'case_type': 'unmatched'})
        c.action_process()
        c.action_resolve()
        c.action_close()
        c.action_reopen()
        self.assertEqual(c.state, 'open')

    def test_05_create_case_line(self):
        c = self.Case.create({'case_type': 'unmatched', 'source': 'auto_matching'})
        cl = self.CaseLine.create({
            'case_id': c.id,
            'issue_amount': 100.0,
        })
        self.assertTrue(cl.id)
        self.assertEqual(len(c.line_ids), 1)
