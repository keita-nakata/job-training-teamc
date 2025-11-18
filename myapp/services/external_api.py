# myapp/services/external_api.py
import requests
from django.conf import settings

def ichiba_item_search(keyword: str, hits: int = 5):
    if not keyword:
        return [], "検索キーワードを入力してください。"
    
    print("DEBUG RAKUTEN_APP_ID:", settings.RAKUTEN_APP_ID)  # ← 一旦確認用
    
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    params = {
                "applicationId": settings.RAKUTEN_APP_ID,
                "keyword": keyword,
                "format": "json",
                "hits": hits, # 取得件数を5件に限定
            }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        items = data.get("Items", [])
        items = [item["Item"] for item in items]

        return items, None  # エラーなし

    except requests.exceptions.RequestException as e:
        return [], f"APIリクエストエラー: {e}"
    except Exception as e:
        return [], f"データの処理中にエラーが発生しました: {e}"
