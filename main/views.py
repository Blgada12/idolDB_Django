from django.shortcuts import render


# Create your views here.
def main_page(req):
    return render(req, 'main/index.html', {})
