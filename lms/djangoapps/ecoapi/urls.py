"""
URLs for mobile WEBAPI
"""
from django.conf.urls import patterns, url, include


# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns(
    '',
    url(r'^users/(?P<id_user>\d+)/courses',  'webapi.views.user_courses', name='webapi_user_courses'),
    url(r'^teachers/(?P<id_teacher>\d+)',  'webapi.views.teacher', name='webapi_teacher'),
    url(r'^heartbeat',  'webapi.views.heartbeat', name='webapi_heartbeat'),
)
