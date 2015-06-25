#-*- coding: utf-8 -*-

import requests, json, datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError


from django.conf import settings
from xapi.models import TrackingLog
from xapi.xapi_tracker import XapiBackend
from django.db.models import Q

class Command(BaseCommand):
    help = 'Export log data stored on the given file to TinCan'

    option_list = BaseCommand.option_list + (
        make_option(
            "-f", 
            "--file", 
            dest = "filename",
            help = "specify import file", 
            metavar = "FILE"
        ),
    )

    def handle(self, *args, **options):
        # make sure file option is present
        if options['filename'] == None :
            raise CommandError("Option `--file=...` must be specified.")
       
        # Open the file, parse it and store the data, if not already present
        filename = options['filename']
        total = 0
        raw_data = open(filename).read()
        lines = [ l.strip() for l in raw_data.split('\n') if l.strip() != '' ]
        TrackingLog.objects.all().delete()
        i=1
        for row in lines:
            event = json.loads(row)
            try:
                dt = datetime.datetime.strptime(event['time'].split('+')[0], '%Y-%m-%dT%H:%M:%S.%f')
                #print i, ' ', dt
                i += 1

            except ValueError:
                print 'Data error -> ',  event['time']
                continue
                                           
            event['context']['user_id'] = 6 #TODO: rimuovere
            event['time'] = dt
            user_id = event['context']['user_id']
            if user_id == '':
                continue
            try:
                t = TrackingLog.objects.get(dtcreated=dt)
                #t = TrackingLog.objects.get(dtcreated=dt, user_id=user_id)
            except TrackingLog.DoesNotExist:
                x = XapiBackend()
                x.send(event)

        """

        options = settings.TRACKING_BACKENDS['xapi']['OPTIONS']
        headers = {
            "Content-Type":"application/json",
            "X-Experience-API-Version":"1.0.0"
        }
        auth = (options['USERNAME_LRS'], options['PASSWORD_LRS'])

        evt_list = TrackingLog.objects.filter(exported=False).filter(tincan_error='').order_by('dtcreated')[:options['EXTRACTED_EVENT_NUMBER']]
        for evt in evt_list:
            resp = requests.post(options['URL'], data=evt.statement, auth=auth, headers=headers)
            try:
                answer = json.loads(resp.content)
                if answer['success'] == False:
                    evt.tincan_error = resp.content
            except:
                evt.tincan_key = resp.content
                evt.exported = True
            evt.save()
        self.stdout.write('Data sent\n')

"""







data = """{"actor": {"objectType": "Agent","account": {"homePage": "https://portal.ecolearning.eu?user=5493fa84cd35f8064e81bcfd","name": "5493fa84cd35f8064e81bcfd"}}, "verb": {"id": "http://activitystrea.ms/schema/1.0/watch","display": {"en-US": "Indicates the learner has watched video xyz"}},
"object": {"objectType": "Activity","id": "http://eco/resourceABC.html","definition": {"name": {"en-US": "Learn something new"},"description": {"en-US": "This is a video about ABC"},"type": "http://activitystrea.ms/schema/1.0/video"}}}"""


