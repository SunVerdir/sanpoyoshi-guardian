import os

os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")

from google.cloud import firestore

_db = None


def get_client() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project="agentic-ai-hackathon-507223")
    return _db


def save_approval_request(plan_summary: str, allocation: dict) -> str:
    """分配案を承認待ちキュー(ApprovalQueue)にステータスPENDING_APPROVALで登録する"""
    db = get_client()
    doc_ref = db.collection("ApprovalQueue").document()
    doc_ref.set(
        {
            "plan_summary": plan_summary,
            "allocation": allocation,
            "status": "PENDING_APPROVAL",
        }
    )
    return doc_ref.id


def get_pending_approvals() -> list[dict]:
    """ApprovalQueueからstatus==PENDING_APPROVALのドキュメントを一覧取得する"""
    db = get_client()
    docs = db.collection("ApprovalQueue").where("status", "==", "PENDING_APPROVAL").stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        results.append(data)
    return results


def update_approval_status(doc_id: str, new_status: str) -> None:
    """ApprovalQueueの該当ドキュメントのstatusを更新する"""
    db = get_client()
    db.collection("ApprovalQueue").document(doc_id).update({"status": new_status})


def get_last_ledger_entry() -> dict | None:
    """Ledgerコレクションの最新エントリを1件取得する。無ければNoneを返す"""
    db = get_client()
    docs = (
        db.collection("Ledger")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def save_ledger_entry(entry: dict) -> None:
    """HashChainLedger.create_log_entry()の戻り値をLedgerコレクションに保存する"""
    db = get_client()
    db.collection("Ledger").add(entry)