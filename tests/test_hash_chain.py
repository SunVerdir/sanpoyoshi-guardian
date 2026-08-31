import unittest
from firestore.hash_chain import HashChainLedger


class TestHashChainLedger(unittest.TestCase):
    def setUp(self):
        self.ledger = HashChainLedger()

        # 1件目のログ生成（申請）
        self.log1 = self.ledger.create_log_entry(
            previous_hash=None,
            action_type="PROPOSE",
            actor="Gemini_Agent",
            details={"proposal_id": "P-001", "amount": 100000}
        )

        # 2件目のログ生成（承認）
        self.log2 = self.ledger.create_log_entry(
            previous_hash=self.log1["current_hash"],
            action_type="APPROVE",
            actor="Staff_001",
            details={"proposal_id": "P-001", "status": "APPROVED"}
        )

    def test_verify_chain_valid(self):
        """正常なチェーンは検証をパスする"""
        chain = [self.log1, self.log2]
        self.assertTrue(self.ledger.verify_chain(chain))

    def test_verify_chain_detects_tampering(self):
        """1件目のdetailsを書き換えると改ざんとして検知される"""
        tampered_chain = [self.log1.copy(), self.log2.copy()]
        tampered_chain[0]["details"] = {"proposal_id": "P-001", "amount": 999999}

        self.assertFalse(self.ledger.verify_chain(tampered_chain))


if __name__ == "__main__":
    unittest.main()