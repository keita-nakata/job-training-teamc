# myapp/services/external_api.py
import requests
from django.conf import settings

ICHIBA_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
BOOKS_URL = "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
GAMES_URL = "https://app.rakuten.co.jp/services/api/BooksGame/Search/20170404"
HOTEL_RANKING_URL = "https://app.rakuten.co.jp/services/api/Travel/HotelRanking/20170426"


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
        "title": keyword,      # ← このAPIは title 検索
        "format": "json",
        "hits": hits,
    }

    try:
        resp = requests.get(GAMES_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        raw_items = [item["Item"] for item in data.get("Items", [])]

        # 👇 Ichiba と同じインターフェースに揃える
        normalized_items = []
        for it in raw_items:
            normalized_items.append({
                # itemName がなければ title を使う
                "itemName": it.get("itemName") or it.get("title") or "",
                "itemUrl": it.get("itemUrl", ""),
                "itemPrice": it.get("itemPrice") or it.get("itemPriceTaxIncl") or "",
            })

        return normalized_items, None

    except requests.exceptions.RequestException as e:
        return [], f"APIリクエストエラー: {e}"
    except Exception as e:
        return [], f"データの処理中にエラーが発生しました: {e}"


def hotel_ranking(genre: str = "all"):
    params = {
        "applicationId": settings.RAKUTEN_APP_ID,
        "format": "json",
        "carrier": 0,
        "genre": genre,       # "all", "onsen", "premium"
        "formatVersion": 2,   # ★ これを付けてフラットな JSON にする
    }

    try:
        resp = requests.get(HOTEL_RANKING_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        rankings = data.get("Rankings", [])
        if not rankings:
            return [], "No ranking data was returned."

        # v1形式だと {"Ranking": {...}} でラップされている可能性があるのでケア
        first = rankings[0]
        ranking_obj = first.get("Ranking", first)

        hotels_raw = ranking_obj.get("hotels", [])

        items = []
        for h in hotels_raw:
            # v1形式だと {"hotel": {...}} でラップされている可能性があるのでケア
            hotel = h.get("hotel", h)

            items.append({
                "rank": hotel.get("rank"),
                "hotelName": hotel.get("hotelName"),
                "middleClassName": hotel.get("middleClassName"),
                "userReview": hotel.get("userReview"),
                "reviewCount": hotel.get("reviewCount"),
                "reviewAverage": hotel.get("reviewAverage"),
                "hotelInformationUrl": hotel.get("hotelInformationUrl"),
                "planListUrl": hotel.get("planListUrl"),
                "checkAvailableUrl": hotel.get("checkAvailableUrl"),
                "reviewUrl": hotel.get("reviewUrl"),
                "hotelImageUrl": hotel.get("hotelImageUrl"),
                "hotelThumbnailUrl": hotel.get("hotelThumbnailUrl"),
            })

        # デバッグ用: ちゃんと入ってるか確認したかったらこれを見る
        # print(items)

        return items, None

    except requests.exceptions.RequestException as e:
        return [], f"APIリクエストエラー: {e}"
    except Exception as e:
        return [], f"データの処理中にエラーが発生しました: {e}"
