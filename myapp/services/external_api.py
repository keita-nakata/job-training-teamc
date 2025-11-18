# myapp/services/external_api.py
import requests
from django.conf import settings

ICHIBA_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
BOOKS_URL = "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
GAMES_URL = "https://app.rakuten.co.jp/services/api/BooksGame/Search/20170404"


def ichiba_item_search(keyword: str, hits: int = 5):
    if not keyword:
        return [], "検索キーワードを入力してください。"

    params = {
        "applicationId": settings.RAKUTEN_APP_ID,
        "keyword": keyword,
        "format": "json",
        "hits": hits,
    }

    try:
        resp = requests.get(ICHIBA_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        items = [item["Item"] for item in data.get("Items", [])]
        return items, None
    except requests.exceptions.RequestException as e:
        return [], f"APIリクエストエラー: {e}"
    except Exception as e:
        return [], f"データの処理中にエラーが発生しました: {e}"


def books_search(keyword: str, hits: int = 5, sort: str | None = None):
    if not keyword:
        return [], "検索キーワードを入力してください。"

    params = {
        "applicationId": settings.RAKUTEN_APP_ID,
        "title": keyword,
        "format": "json",
        "hits": hits,
    }
    if sort:
        params["sort"] = sort

    try:
        resp = requests.get(BOOKS_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        items = [item["Item"] for item in data.get("Items", [])]
        return items, None
    except requests.exceptions.RequestException as e:
        return [], f"APIリクエストエラー: {e}"
    except Exception as e:
        return [], f"データの処理中にエラーが発生しました: {e}"

def games_search(keyword: str, hits: int = 5):
    if not keyword:
        return [], "検索キーワードを入力してください。"

    params = {
        "applicationId": settings.RAKUTEN_APP_ID,
        "title": keyword,
        "format": "json",
        "hits": hits,
    }

    try:
        resp = requests.get(GAMES_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        items = [item["Item"] for item in data.get("Items", [])]
        return items, None
    except requests.exceptions.RequestException as e:
        return [], f"APIリクエストエラー: {e}"
    except Exception as e:
        return [], f"データの処理中にエラーが発生しました: {e}"