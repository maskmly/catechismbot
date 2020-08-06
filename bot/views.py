from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from . import main


# Create your views here.
@csrf_exempt
def catechismbot(request):
    if request.method == 'POST':
        payload = request.body.decode('utf8')
        main.process(main.get_json(payload))
        return HttpResponse('Ok')
    else:
        return HttpResponse('Are you lost brother?\n')


