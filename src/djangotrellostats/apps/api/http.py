
from django.http import HttpResponse


class HttpResponseMethodNotAllowed(HttpResponse):
    status_code = 405