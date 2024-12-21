from django.http import JsonResponse

def home(request) -> JsonResponse:
    return JsonResponse({'details':'welcome to the devtube'},status=200)