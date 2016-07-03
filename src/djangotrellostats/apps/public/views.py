from django.shortcuts import render


def index(request):
    replacements = {}
    return render(request, "public/index.html", replacements)

