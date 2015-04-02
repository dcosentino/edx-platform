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

ACCESS_VERB = {
    "id": "http://activitystrea.ms/schema/1.0/access",
    "display": { "en-US": "Indicates the learner accessed something" }
}
SUBMIT_VERB = {
    "id": "http://activitystrea.ms/schema/1.0/submit",
    "display": { "en-US": "Indicates the learner submitted something" }
}

EDX2TINCAN = {
    'learner_accesses_MOOC': ACCESS_VERB,
    'learner_accesses_a_module': ACCESS_VERB,

    ################# ASSESSMENT ################################
    'learner_accesses_assessment': ACCESS_VERB,
    'learner_answers_question': {
        "id": "http://adlnet.gov/expapi/verbs/answered",
        "display": { "en-US": "Indicates the learner answered a question" }
    },

    ################# PEER ASSESSMENT ###########################
    'learner_accesses_peer_assessment': ACCESS_VERB,
    'learner_submits_assessment': SUBMIT_VERB,
    'learner_submits_peer_feedback': SUBMIT_VERB,
    'learner_submits_peer_product': SUBMIT_VERB,

    ################# FORUM #####################################
    'learner_accesses_forum': ACCESS_VERB,
    'learner_post_new_forum_thread': {
        "id": "http://activitystrea.ms/schema/1.0/author",
        "display": { "en-US": "Indicates the learner authored something" }
    },
    'learner_replies_to_forum_message': {
        "id": "http://adlnet.gov/expapi/verbs/commented",
        "display": { "en-US": "Indicates the learner commented on something" }
    },
    'learner_liked_forum_message': {
        "id": "http://activitystrea.ms/schema/1.0/like",
        "display": { "en-US": "Indicates the learner liked a forum message" }
    },
    'learner_reads_forum_message': {
        "id": "http://activitystrea.ms/schema/1.0/read",
        "display": { "en-US": "Indicates the learner read a forum message" }
    },

    ################# ASSIGNMENT #################################
    # NOT USED 'learner_accesses_assignment': ACCESS_VERB,
    # NOT USED 'learner_submit_assignment': ACCESS_VERB,

    ################# WIKI #######################################
    'learner_accesses_wiki': ACCESS_VERB,
    'learner_accesses_wiki_page': ACCESS_VERB,
    'learner_creates_wiki_page': {
        "id": "http://activitystrea.ms/schema/1.0/create",
        "display": { "en-US": "Indicates the learner created something" }
    },
    'learner_edits_wiki_page': {
        "id": "http://activitystrea.ms/schema/1.0/update",
        "display": { "en-US": "Indicates the learner updated or edited something" }
    },
    ################# VIDEO ######################################
    'play_video': {
        "id": "http://activitystrea.ms/schema/1.0/watch",
        "display": { "en-US": "Indicates the learner has watched video xyz" }
    }
}

class TrackingLog(models.Model):
    """This model defines the fields that are stored in the tracking log database."""

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
        self.oai_prefix = options.get('OAI_PREFIX', '')
        self.name = name


    # Vedi https://github.com/adlnet/edx-xapi-bridge/blob/master/xapi-bridge/converter.py
    def to_xapi(self, evt, course_id):
        #evt['time'] = evt['time'].strftime("%Y-%m-%dT%H:%M:%S")
        #return evt
        action = {}
        obj = {}
        
        usereco = self.get_actor(evt['context']['user_id'])
          
        if re.match('^/courses/[/\w]+/info/?', evt['event_type']):
            # Learner accesses MOOC
            action = EDX2TINCAN['learner_accesses_MOOC']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['event_type'], 
                "definition": {
                    "name": { "en-US": self.oai_prefix + course_id },
                    "type": "http://adlnet.gov/expapi/activities/course"
                }
            }
            
        #elif evt['event_type'] == u'/courses/edX/DemoX/Demo_Course/courseware/d8a6192ade314473a78242dfeedfbf5b/edx_introduction/':
        elif re.match('^/courses[/\w]+/courseware/\w+', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_a_module']
            module = evt['event_type'].split('/')[-2:][0]
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": module },
                    "type": "http://adlnet.gov/expapi/activities/module"
                }
            }

        elif re.match('/courses[/\w]+/wiki/\w+/_create/?', evt['event_type']):
            title = None
            try: 
                event_data = json.loads(evt['event']) # We need to do this because we receive a string instead than a dictionary
                title = event_data['POST'].get('title', None)
            except:
                pass
            if title:
                action = EDX2TINCAN['learner_creates_wiki_page']
                obj = {
                    "objectType": "Activity",
                    "id": self.base_url + evt['context']['path'],
                    "definition": {
                        "name": { "en-US": title },
                        "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                    }
                }
            else:
                action = None # Skip the not really created pages
        elif re.match('/courses[/\w]+/wiki[/\w]+/_edit/?', evt['event_type']):
            # EX: /courses/edX/DemoX/Demo_Course/wiki/DemoX/_edit/ or
            #     /courses/edX/DemoX/Demo_Course/wiki/DemoX/page/_edit/
            title = None
            try: 
                event_data = json.loads(evt['event']) # We need to do this because we receive a string instead than a dictionary
                title = event_data['POST'].get('title', None)
            except:
                pass
            if title:
                action = EDX2TINCAN['learner_edits_wiki_page']
                obj = {
                    "objectType": "Activity",
                    "id": self.base_url + evt['context']['path'],
                    "definition": {
                        "name": { "en-US": title },
                        "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                    }
                }
            else:
                action = None # Skip the not really edited pages

        elif re.match('/courses[/\w]+/wiki/\w+/\w+/?', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_wiki_page']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['context']['path'] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }
        elif re.match('/courses[/\w]+/wiki/\w+/?', evt['event_type']):
            action = EDX2TINCAN['learner_accesses_wiki']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['context']['path'] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }
            
        ########################### ASSESSMENT ################################################
        elif re.match('^/courses/[/:;_\w]+/problem_get/?', evt['event_type']) and evt['event_source'] == 'server':
            action = EDX2TINCAN['learner_accesses_assessment']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'], # TODO: cosa ci mettiamo? non sembra ci sia nient'altro di utile
                # Il self.path è stato aggiunto per poter risolvere l'errore "id is not a valid IRI in object" ricevuto dall'LRS
                "definition": {
                    "name": { "en-US": evt['context']['path'] },
                    "type": "http://adlnet.gov/expapi/activities/question"
                }
            }
        # We check event_source because this event is registered twice (browser and server)
        elif evt['event_type'] == 'problem_check' and evt['event_source'] == 'server':
            action = EDX2TINCAN['learner_answers_question']
            obj = {
                "objectType": "Activity",
                "id": evt['event']['problem_id'],
                "definition": {
                    "name": { "en-US": evt['context']['module']['display_name'] },
                    "type": "http://adlnet.gov/expapi/activities/question"
                }
            }
        ########################### END ASSESSMENT #############################################


        ########################### VIDEO ######################################################
        elif evt['event_type'] == 'play_video' and evt['event_source'] == 'browser':
            action = EDX2TINCAN['play_video']
            try:
                event = json.loads(evt['event']) # We need to do this because we receive a string instead than a dictionary
                obj = {
                    "objectType": "Activity",
                    "id": evt['page'],
                    "definition": {
                        "name": { "en-US": event['id'] },
                        "type": "http://activitystrea.ms/schema/1.0/video"
                    }
                }
            except:
                action = None # No event data, just skip
        ########################### END VIDEO ##################################################

        ############################ FORUM #####################################################

        elif re.match('/courses[/\S]+/discussion/[\S]+/create/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/i4x-Polimi-MAT101-2015_M2/threads/create
            title = None
            try: 
                event_data = json.loads(evt['event']) # We need to do this because we receive a string instead than a dictionary
                title = event_data['POST'].get('title', None)
            except:
                pass
            if title:

                action = EDX2TINCAN['learner_post_new_forum_thread']
                obj = {
                    "objectType": "Activity",
                    "id": self.base_url + evt['context']['path'],
                    "definition": {
                        "name": { "en-US": title },
                        "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                    }
                }
            else:
                action = None # Skip the not really created post

        elif re.match('/courses[/\S]+/discussion/[\S]+/reply/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/i4x-Polimi-MAT101-2015_M2/threads/create
            action = EDX2TINCAN['learner_replies_to_forum_message']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'].split('reply')[0] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        elif re.match('/courses[/\S]+/discussion/[\S]+/upvote/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/i4x-Polimi-MAT101-2015_M2/threads/create
            action = EDX2TINCAN['learner_liked_forum_message']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'].split('upvote')[0] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        elif re.match('/courses[/\S]+/discussion/[\S]+/threads/[\S]+/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/forum/i4x-Polimi-MAT101-2015_M2/threads/5519ab9656c02c3e9f000005
            action = EDX2TINCAN['learner_reads_forum_message']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }

        elif re.match('/courses[/\S]+/discussion/\w+/?', evt['event_type']):
            # Ex: /courses/Polimi/mat101/2012_01/discussion/forum
            action = EDX2TINCAN['learner_accesses_forum']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'] }, 
                    "type": "http://www.ecolearning.eu/expapi/activitytype/wiki"
                }
            }
         
        ########################## END FORUM ###################################################


        ########################## PEER ASSESSMENT #############################################
        elif re.match('/courses/[\S]+/render_peer_assessment/?', evt['event_type']):
            # Ex: /courses/edX/DemoX/Demo_Course/xblock/i4x:;_;_edX;_DemoX;_openassessment;_b24c33ea35954c7889e1d2944d3fe397/handler/render_peer_assessment
            action = EDX2TINCAN['learner_accesses_peer_assessment']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'].split('render_peer_assessment')[0] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        elif re.match('/courses/[\S]+/submit/?', evt['event_type']):
            # Ex: /courses/edX/DemoX/Demo_Course/xblock/i4x:;_;_edX;_DemoX;_openassessment;_b24c33ea35954c7889e1d2944d3fe397/handler/submit
            action = EDX2TINCAN['learner_submits_assessment']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'].split('submit')[0] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        elif re.match('/courses/[\S]+/peer_assess/?', evt['event_type']):
            # Ex: /courses/edX/DemoX/Demo_Course/xblock/i4x:;_;_edX;_DemoX;_openassessment;_b24c33ea35954c7889e1d2944d3fe397/handler/peer_assess
            action = EDX2TINCAN['learner_submits_peer_feedback']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'].split('peer_assess')[0] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }

        elif re.match('/courses/[\S]+/self_assess/?', evt['event_type']):
            # Ex: /courses/edX/DemoX/Demo_Course/xblock/i4x:;_;_edX;_DemoX;_openassessment;_b24c33ea35954c7889e1d2944d3fe397/handler/self_assess
            action = EDX2TINCAN['learner_submits_peer_product']
            obj = {
                "objectType": "Activity",
                "id": self.base_url + evt['context']['path'],
                "definition": {
                    "name": { "en-US": evt['event_type'].split('self_assess')[0] },
                    "type": "http://www.ecolearning.eu/expapi/activitytype/peerassessment"
                }
            }



        ########################## END PEER ASSESSMENT #########################################


        # List of not recorded actions
        elif evt['event_type'] == 'page_close':
            action = None
        elif evt['event_type'] == 'problem_graded':
            action = None
        elif re.match('problem_check$', evt['event_type']):
            action = None
        else:
            # Only for test and debug
            # print '-> EVENT NOT MANAGED: ', evt
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
        if course_id is None or course_id == '':
            try:
                event = json.loads(event_edx['event']) # We need to do this because we receive a string instead than a dictionary
                course_id = event['POST'].get('course_id', None)[0]
            except:
                pass # No event data, just skip

        if course_id in self.course_ids:
            try:
                # Sometimes we receive time as python datetime, sometimes as string...
                try:
                    timestamp = event_edx['time'].strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    timestamp = event_edx['time']
                    
                verb, obj = self.to_xapi(event_edx, course_id)
                # verb = None means to not record the action
                if verb:
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
