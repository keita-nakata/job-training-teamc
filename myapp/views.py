from django.views.generic import TemplateView
from django.shortcuts import render
from .services.external_api import ichiba_item_search

# Create your views here.

class ApiTestView(TemplateView):
    template_name = "myapp/api_test.html"

    def get_context_data(self, **kwargs):
        # GET（初期表示）のときのデフォルト値
        context = super().get_context_data(**kwargs)
        context.setdefault("items", [])
        context.setdefault("search_keyword", None)
        context.setdefault("error_message", None)
        return context

    def post(self, request, *args, **kwargs):
        # フォームからキーワード取得
        search_keyword = request.POST.get("keyword", "")

        # ここで external_api の共通関数を呼ぶ！
        items, error_message = ichiba_item_search(search_keyword, hits=5)

        # context を組み立ててテンプレートに渡す
        context = self.get_context_data(
            items=items,
            search_keyword=search_keyword,
            error_message=error_message,
        )
        return self.render_to_response(context)