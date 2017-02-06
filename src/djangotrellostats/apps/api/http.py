
from django.http import HttpResponse, JsonResponse


class HttpResponseMethodNotAllowed(HttpResponse):
    status_code = 405


class JsonResponseMethodNotAllowed(JsonResponse):
    status = 405
    status_code = 405


class JsonResponseBadRequest(JsonResponse):
    status = 400
    status_code = 400


class JsonResponseNotFound(JsonResponse):
    status = 404
    status_code = 404
