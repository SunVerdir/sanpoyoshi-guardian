import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class HashChainLedger:
    def __init__(self):
        self.GENESIS_HASH = "0" * 64

    def calculate_hash(self, previous_hash: str, action_type: str, actor: str, details: Dict[str, Any], timestamp: str) -> str:
        """直前のハッシュ値と今回のログデータを結合してSHA-256ハッシュ値を算出"""
        payload = {
            "previous_hash": previous_hash,
            "action_type": action_type,
            "actor": actor,
            "details": details,
            "timestamp": timestamp
        }
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def create_log_entry(self, previous_hash: Optional[str], action_type: str, actor: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """新規ログドキュメントの生成"""
        prev_hash = previous_hash if previous_hash else self.GENESIS_HASH
        now_utc = datetime.now(timezone.utc).isoformat()
        
        current_hash = self.calculate_hash(
            previous_hash=prev_hash,
            action_type=action_type,
            actor=actor,
            details=details,
            timestamp=now_utc
        )

        return {
            "previous_hash": prev_hash,
            "current_hash": current_hash,
            "action_type": action_type, # 例: 'PROPOSE', 'APPROVE'
            "actor": actor,             # 例: 'Gemini_Agent', 'Staff_001'
            "details": details,
            "timestamp": now_utc
        }

    def verify_chain(self, logs: list) -> bool:
        """取得したログ一覧のハッシュチェーン改ざん検証"""
        for i in range(len(logs)):
            current = logs[i]
            expected_prev_hash = logs[i-1]["current_hash"] if i > 0 else self.GENESIS_HASH
            
            # 1. 直前ハッシュの不整合チェック
            if current["previous_hash"] != expected_prev_hash:
                print(f"[改ざん検知] ログインデックス {i} の previous_hash が一致しません。")
                return False

            # 2. データの再ハッシュ化・照合チェック
            recalculated = self.calculate_hash(
                previous_hash=current["previous_hash"],
                action_type=current["action_type"],
                actor=current["actor"],
                details=current["details"],
                timestamp=current["timestamp"]
            )
            if recalculated != current["current_hash"]:
                print(f"[改ざん検知] ログインデックス {i} のデータ内容が改ざんされています。")
                return False

        return True