# myapp/views.py
from django.views.generic import TemplateView
from .services.external_api import ichiba_item_search, books_total_search


class ApiTestView(TemplateView):
    template_name = "myapp/api_test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 楽天市場
        context.setdefault("ichiba_items", [])
        context.setdefault("ichiba_search_keyword", None)
        context.setdefault("ichiba_error_message", None)

        # 楽天ブックス
        context.setdefault("books_items", [])
        context.setdefault("books_search_keyword", None)
        context.setdefault("books_error_message", None)

        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")  # "ichiba" or "books"

        # 初期値
        ichiba_items = []
        ichiba_search_keyword = None
        ichiba_error_message = None

        books_items = []
        books_search_keyword = None
        books_error_message = None

        if form_type == "ichiba":
            ichiba_search_keyword = request.POST.get("keyword", "")
            ichiba_items, ichiba_error_message = ichiba_item_search(
                ichiba_search_keyword, hits=5
            )

        elif form_type == "books":
            books_search_keyword = request.POST.get("keyword", "")
            books_items, books_error_message = books_total_search(
                books_search_keyword,
                hits=5,
                # 例: "+itemPrice"（安い順）など。不要なら省略可。
                # sort="+itemPrice",
            )

        context = self.get_context_data(
            ichiba_items=ichiba_items,
            ichiba_search_keyword=ichiba_search_keyword,
            ichiba_error_message=ichiba_error_message,
            books_items=books_items,
            books_search_keyword=books_search_keyword,
            books_error_message=books_error_message,
        )
        return self.render_to_response(context)
