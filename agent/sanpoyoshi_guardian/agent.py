from google.adk.agents import Agent


def fetch_cafeteria_demands() -> dict:
    """近隣子ども食堂の在庫状況・過去1か月の受領履歴を返す。"""
    return {
        "食堂A": {"capacity": 30, "received_this_week_kg": 2.0},
        "食堂B": {"capacity": 50, "received_this_week_kg": 0.0},
    }


def compute_distribution_ratio(item_name: str, quantity_kg: float, demands: dict) -> dict:
    """食堂ごとの需要データから、機械的な分配比率（kg数）を算出する。

    ロジック: 受入容量が大きく、かつ直近の受領量が少ない食堂ほど多く配分する。
    """
    scores = {}
    for name, data in demands.items():
        capacity = data["capacity"]
        received = data["received_this_week_kg"]
        # 容量が大きいほど、受領量が少ないほどスコアが高い
        scores[name] = max(capacity - received * 5, 1)

    total_score = sum(scores.values())
    allocation = {
        name: round(quantity_kg * score / total_score, 1)
        for name, score in scores.items()
    }
    return {"item_name": item_name, "quantity_kg": quantity_kg, "allocation": allocation}


def create_approval_request(plan_summary: str, allocation_json: str) -> str:
    """分配案を承認待ちキューに登録する（現時点は仮実装で標準出力にログするのみ）。"""
    print("\n[APPROVAL QUEUE CREATED] status=PENDING_APPROVAL")
    print(f"  plan_summary: {plan_summary}")
    print(f"  allocation_json: {allocation_json}")
    return "REQUEST_CREATED_ID_98765"


root_agent = Agent(
    model="gemini-2.5-flash",
    name="sanpoyoshi_guardian",
    description="Metaマルシェの規格外品出品を監視し、子ども食堂への分配案を自律的に起案するエージェント",
    instruction=(
        "規格外品が出品されたら、次の手順で対応してください。"
        "1. fetch_cafeteria_demands で各食堂の状況を確認する。"
        "2. compute_distribution_ratio で機械的な分配比率を算出する。"
        "3. 算出結果をもとに、議会・自治体向けの理由説明文をあなた自身の言葉で作成する。"
        "4. create_approval_request を呼び出し、理由説明文と分配案（JSON文字列）を渡して承認待ちに登録する。"
        "5. 最後に、職員へ向けて分配案・理由・承認待ちである旨を分かりやすくまとめて報告する。"
        "支出の最終決定はあなたが行わず、必ず職員の承認を待つことを明言してください。"
    ),
    tools=[fetch_cafeteria_demands, compute_distribution_ratio, create_approval_request],
)