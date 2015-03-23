# -*- coding: utf-8 -*-
"""
Event tracker backend that saves events to a Django database.
"""

# TODO: this module is very specific to the event schema, and is only
# brought here for legacy support. It should be updated when the
# schema changes or eventually deprecated.

from __future__ import absolute_import

import logging, datetime, json

from django.db import models

from track.backends import BaseBackend
from xmodule_django.models import CourseKeyField
# TODO: è giusto? era così:
#log = logging.getLogger('track.backends.django')
log = logging.getLogger('xapi.xapi_tracker')


LOGFIELDS = [
    'user_id',
    'course_id',
    'statement',
]


class TrackingLog(models.Model):
    """Defines the fields that are stored in the tracking log database."""

    dtcreated = models.DateTimeField('creation date', auto_now_add=True)
    user_id = models.IntegerField(blank=True)
    course_id = CourseKeyField(max_length=255, blank=True)
    statement = models.TextField(blank=True)
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
        self.name = name



    # Vedi https://github.com/adlnet/edx-xapi-bridge/blob/master/xapi-bridge/converter.py
    def to_xapi(self, evt):
        # TODO: completare e qui recuperare lo user e il course id corretti
        print 'to_xapi: ' 
        evt['time'] = evt['time'].strftime("%Y-%m-%dT%H:%M:%S")
        return evt
        statement = {}
        
        if evt['event_type'] == '/login_ajax':
            statement['action'] = 'Login'
        
        return statement



    def send(self, event_edx):
        print 'send: ', event_edx

        # TODO: LO SWITCH VA QUI
        statement = json.dumps(self.to_xapi(event_edx))
        tldat = TrackingLog(
            dtcreated = event_edx['time'],
            user_id = event_edx['context']['user_id'],
            course_id = event_edx['context']['course_id'],
            statement= statement
        )
        tldat.save() # TODO: scommentare

        # TODO: è qui che devo mettere il mega switch o in views (meglio views, che ha anche la request)?
        # Stanford però mette qui...
        # va aggiunto anche il test per evitare la duplicazione delle insert


        try:
            tldat.save(using=self.name)
        except Exception as e:  # pylint: disable=broad-except
            log.exception(e)
