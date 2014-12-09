#-*- coding: utf-8 -*-
import datetime, json
from django.http import HttpResponse
from django.conf import settings



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

    risposta = {
        "name": "Darth Vader",
        "imageUrl":"http:a.b.c/images/me.jpg",
        "desc": [
            {
                "language":"en",
                "label":"Darth is a very populair guy, despite his appearance"
            },
            {
                "language":"fr",
                "label":"Darth est un gars très populaire, malgré  son apparence"
            }
        ]
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
