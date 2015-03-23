# -*- coding: utf-8 -*-
import json 
from track import tracker

def merge(d1,d2):
    if isinstance(d1,dict) and isinstance(d2,dict):
        final = {}
        for k,v in d1.items()+d2.items():
            if k not in final:
                final[k] = v
            else:
                final[k] = merge(final[k], v)

                return final
	
    elif d2 != None:
        return d2
	
    else:
        return d1



def log_event(event):
    """Capture a event by sending it to the register trackers"""
    tracker.send(event)



# Vedi https://github.com/adlnet/edx-xapi-bridge/blob/master/xapi-bridge/converter.py
def to_xapi(evt, event_type):
    # TODO: completare
    print 'to_xapi: ' 

    statement = {}

    if event_type == '/login_ajax':
        statement['action'] = 'Login'
        
    return statement

def server_track(request, event_type, event, page=None):
    """
    Log events related to server requests.
    Handle the situation where the request may be NULL, as may happen with management commands.
    """
    # TODO: è qui che devo mettere il mega switch o in xapi_tracker?
    
    print 'server_track, ', event['event_type'], event['event_source']

    event['statement'] = json.dumps(to_xapi(event, event_type))
    print event['statement']
    event['user_id'] = 42
    event['course_id'] = 42
    

    log_event(event)
