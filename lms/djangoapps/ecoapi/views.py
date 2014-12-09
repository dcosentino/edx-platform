#-*- coding: utf-8 -*-
import datetime, json
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from models import *

class JsonResponse(HttpResponse):
    def __init__(self, content={}, mimetype=None, status=None,
             content_type='application/json'):
        super(JsonResponse, self).__init__(json.dumps(content), mimetype=mimetype,
                                           status=status, content_type=content_type)



def heartbeat(request):
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    risposta = {
        "alive_at": now
    }

    return JsonResponse(risposta)


def teacher(request, id_teacher):

    teacher = get_object_or_404(Teacher, id=id_teacher)
    name = u'%s %s' % (teacher.first_name, teacher.last_name)
    if teacher.image:
        imageurl = teacher.image.url # TODO: prefisso col dominio
    else:
        imageurl = ''

    descriptions = []
    for d in teacher.teacherdescription_set.all():
        descriptions.append(
            { "language": d.language,
              "label": d.label
            }
        )
    risposta = {
        "name": name,
        "imageUrl": imageurl,
        "desc": descriptions
    }
    return JsonResponse(risposta)


def user_courses(request, id_user):

    risposta =  [
        {
            "id": "0470F4C2DCEB689A",
            "progressPercentage": 25, 
            "spentTime": 36000, 
            "viewCount": 3, 
            "firstViewDate": "2014-10-14T06:00:00Z", 
            "lastViewDate": "2014-10-14T06:10:00Z", 
            "completedDate": "" 
            
        },
        
        {
            "id": "0470F",
            "currentpill":3 , 
            "spentTime": 36000, 
            "viewCount": 3, 
            "firstViewDate": "2014-10-14T06:00:00Z", 
            "lastViewDate": "2014-10-14T06:10:00Z", 
            "completedDate": "" 
        }
    ]
    return JsonResponse(risposta)
