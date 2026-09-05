from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from firestore.firestore_client import (
    get_pending_approvals,
    update_approval_status,
    get_last_ledger_entry,
    save_ledger_entry,
)
from firestore.hash_chain import HashChainLedger

st.set_page_config(page_title="三方よしガーディアン 承認ダッシュボード", layout="wide")
st.title("承認待ちキュー")

STAFF_ID = "Staff_001"  # 暫定：ログイン機能実装前の固定値

pending = get_pending_approvals()

if not pending:
    st.info("現在、承認待ちの分配案はありません。")
else:
    for item in pending:
        with st.container(border=True):
            st.subheader(item.get("plan_summary", "（概要なし）"))
            st.json(item.get("allocation", {}))
            if st.button("承認する", key=f"approve_{item['doc_id']}"):
                # 1. ApprovalQueueのステータス更新
                update_approval_status(item["doc_id"], "APPROVED")

                # 2. Ledgerへの記帳
                ledger = HashChainLedger()
                last_entry = get_last_ledger_entry()
                previous_hash = last_entry["current_hash"] if last_entry else None

                new_entry = ledger.create_log_entry(
                    previous_hash=previous_hash,
                    action_type="APPROVE",
                    actor=STAFF_ID,
                    details={
                        "doc_id": item["doc_id"],
                        "allocation": item.get("allocation", {}),
                        "status": "APPROVED",
                    },
                )
                save_ledger_entry(new_entry)

                st.success(f"承認しました（doc_id: {item['doc_id']}）")
                st.rerun()