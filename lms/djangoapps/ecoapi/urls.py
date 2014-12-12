"""
URLs for mobile WEBAPI
"""
from django.conf.urls import patterns, url, include


# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns(
    '',
    url(r'^users/(?P<id_user>\d+)/courses',  'ecoapi.views.user_courses', name='ecoapi_user_courses'),
    url(r'^teachers/(?P<id_teacher>\d+)',  'ecoapi.views.teacher_view', name='ecoapi_teacher'),
    url(r'^heartbeat',  'ecoapi.views.heartbeat', name='ecoapi_heartbeat'),
)
