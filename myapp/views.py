from django.shortcuts import render

# Create your views here.

class ApiTestView:
    def get(self, request):
        return render(request, 'api_test.html')