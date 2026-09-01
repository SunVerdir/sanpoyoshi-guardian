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
    """分配案を承認待ちキュー(ApprovalQueue)にステータスPENDING_APPROVALで登録する。"""
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