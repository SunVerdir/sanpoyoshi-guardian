from google.adk.agents import Agent


def fetch_cafeteria_demands() -> dict:
    """近隣子ども食堂の在庫状況・過去1か月の受領履歴を返す。"""
    return {
        "食堂A": {"capacity": 30, "received_this_week_kg": 2.0},
        "食堂B": {"capacity": 50, "received_this_week_kg": 0.0},
    }


root_agent = Agent(
    model="gemini-2.5-flash",
    name="sanpoyoshi_guardian",
    description="Metaマルシェの規格外品出品を監視し、子ども食堂への分配案を自律的に起案するエージェント",
    instruction=(
        "規格外品が出品されたら、fetch_cafeteria_demands を呼び出して"
        "各食堂の状況を確認し、どちらの食堂に多く配分すべきか、"
        "理由とともに日本語で説明してください。"
    ),
    tools=[fetch_cafeteria_demands],
)