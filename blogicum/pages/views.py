from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.


def handler404(request: HttpRequest, exception: Exception):
    return render(request, "pages/404.html", status=404)


def handler500(request: HttpRequest):
    return render(request, "pages/500.html", status=500)


def handler403csrf(request: HttpRequest, reason=""):
    return render(request, "pages/403csrf.html", status=403)
