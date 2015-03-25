# -*- coding: utf-8 -*-
"""
Event tracker backend that saves events to a Django database.
"""

# TODO: this module is very specific to the event schema, and is only
# brought here for legacy support. It should be updated when the
# schema changes or eventually deprecated.

from __future__ import absolute_import

import logging, datetime, json, re

from django.db import models

from track.backends import BaseBackend
from xmodule_django.models import CourseKeyField

from django.conf import settings
from social.apps.django_app.default.models import UserSocialAuth

# TODO: è giusto? era così:
#log = logging.getLogger('track.backends.django')
log = logging.getLogger('xapi.xapi_tracker')


LOGFIELDS = [
    'user_id',
    'course_id',
    'statement',
]

EDX2TINCAN = {
    'learner_accesses_MOOC': {
        "id": "http://activitystrea.ms/schema/1.0/access",
        "display": {
            "en-US": "Indicates the learner accessed something"
        }
    },
    'learner_accesses_a_module': {
        "id": "http://activitystrea.ms/schema/1.0/access",
        "display": {
            "en-US": "Indicates the learner accessed something"
        }
    },
    'learner_answers_question': {
        "id": "http://adlnet.gov/expapi/verbs/answered",
        "display": {
            "en-US": "Indicates the learner answered a question"
        }
    },
    'play_video': {
        "id": "http://activitystrea.ms/schema/1.0/watch",
        "display": {
            "en-US": "Indicates the learner has watched video xyz"
        }
    }
}

class TrackingLog(models.Model):
    """Defines the fields that are stored in the tracking log database."""

    dtcreated = models.DateTimeField('creation date', auto_now_add=True)
    user_id = models.IntegerField(blank=True)
    course_id = CourseKeyField(max_length=255, blank=True)
    statement = models.TextField(blank=True)
    tincan_key = models.CharField(max_length=512, null=True, blank=True)
    tincan_error = models.TextField(blank=True, null=True, default='')
    exported = models.BooleanField(default=False)

    class Meta:
        app_label = 'xapi'
        db_table = 'xapi_trackinglog'

    def __unicode__(self):
        fmt = (
            u"[{self.dtcreated}] {self.user_id}@{self.course_id}: "
        )
        return fmt.format(self=self)





class XapiBackend(BaseBackend):
    """Event tracker backend that saves to a Django database"""
    def __init__(self, name='default', **options):
        """
        Configure database used by the backend.
        :Parameters:
          - `name` is the name of the database as specified in the project
            settings.
        """

        super(XapiBackend, self).__init__(**options)

        self.course_ids = set(options.get('ID_COURSES', []))
        self.base_url = options.get('BASE_URL', '')
        self.name = name



    # Vedi https://github.com/adlnet/edx-xapi-bridge/blob/master/xapi-bridge/converter.py
    def to_xapi(self, evt):
        # TODO: completare e qui recuperare lo user e il course id corretti

        # TODO: LO SWITCH VA QUI

        #evt['time'] = evt['time'].strftime("%Y-%m-%dT%H:%M:%S")
        #return evt
        action = {}
        obj = {}
        
        # todo: metterlo 
        usereco = self.get_actor(evt['context']['user_id'])
        try:
            event = json.loads(evt['event']) # We need to do this because we receive a string instead than a dictionary
        except ValueError:
            pass # No event data, just skip
            
        print evt

        #if evt['event_type'] == u'/courses/edX/DemoX/Demo_Course/info':
        if re.match('^/courses/[/\w]+/info/?', evt['event_type']):
            # Learner accesses MOOC
            action = EDX2TINCAN['learner_accesses_MOOC']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['event_type'], # TODO: aggiungere url da settings
                "definition": {
                    "name": {
                        "en-US": "The XYZ MOOC"
                    },
                    "description": {
                        "en-US": "This is a MOOC about XYZ"
                    },
                    "type": "http://adlnet.gov/expapi/activities/course"
                }
            }
            
        #elif evt['event_type'] == u'/courses/edX/DemoX/Demo_Course/courseware/d8a6192ade314473a78242dfeedfbf5b/edx_introduction/':
        elif re.match('^/courses[/\w]+/courseware/\w+', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_a_module']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": {
                        "en-US": "Module ABC"
                    },
                    "description": {
                        "en-US": "This is a module about XYZ"
                    },
                    "type": "http://adlnet.gov/expapi/activities/module"
                }
            }

        elif evt['event_type'] == 'problem_graded':
            action = EDX2TINCAN['learner_answers_question']
            obj = {
                "objectType": "Activity",
                "id": evt['page'],
                "definition": {
                    "name": {
                        "en-US": "The operating system"
                    },
                    "description": {
                        "en-US": "This is a question"
                    },
                    "type": "http://adlnet.gov/expapi/activities/question"
                }
            }

        elif evt['event_type'] == 'play_video':
            action = EDX2TINCAN['play_video']
            obj = {
                "objectType": "Activity",
                #"id": event['id'],
                "id": evt['page'],
                "definition": {
                    "name": {
                        "en-US": "Learn something new"
                    },
                    "description": {
                        "en-US": "This is a video about ABC"
                    },
                    "type": "http://activitystrea.ms/schema/1.0/video"
                }
            }
        else:
            # Only for test and debug
            evt['time'] = evt['time'].strftime("%Y-%m-%dT%H:%M:%S")
            action = evt
        return action, obj


    def get_actor(self, username):
        # View http://192.168.33.10:8000/admin/default/usersocialauth/
        # No need to check existance, because is mandatory
        usereco = UserSocialAuth.objects.get(user=username)

        actor = {
            "objectType": "Agent",
            "account": {
            "homePage": "https://portal.ecolearning.eu?user=%s" % usereco.uid,
                "name": usereco.uid
            }
        }
        return actor


    def send(self, event_edx):

        course_id = event_edx['context'].get('course_id', None)
        if course_id in self.course_ids:
            try:
                # Sometimes we receive time as python datetime, sometimes as string...
                try:
                    timestamp = event_edx['time'].strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    timestamp = event_edx['time']

                verb, obj = self.to_xapi(event_edx)
                statement = {
                    'actor': self.get_actor(event_edx['context']['user_id']),
                    'verb': verb,
                    'object': obj,
                    'timestamp': timestamp
                }
          
                statement = json.dumps(statement)

                tldat = TrackingLog(
                    dtcreated = event_edx['time'],
                    user_id = event_edx['context']['user_id'], 
                    course_id = course_id,
                    statement= statement
                )
           
                # We don't need to add duplication event test, so we save directly
                tldat.save()

            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
