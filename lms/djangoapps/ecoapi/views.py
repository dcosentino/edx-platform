#-*- coding: utf-8 -*-
import datetime
import json
from datetime import timedelta
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import UTC
from social.apps.django_app.default.models import UserSocialAuth
from courseware import grades
from courseware.models import StudentModule , OfflineComputedGrade
from courseware.courses import get_course_by_id
from models import Teacher
from tasks import offline_calc
import time

class JsonResponse(HttpResponse):
    """
    Wrapper for HttpResponse with the right content type and the dump to json.
    """
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


def teacher_view(request, id_teacher):
    try:
        teacher = get_object_or_404(Teacher, id_teacher=id_teacher)
    except Http404:
        emptyresponse = {}
        return JsonResponse(emptyresponse)
    name = u'%s %s' % (teacher.first_name, teacher.last_name)
    if teacher.image:
        imageurl = teacher.image
    else:
        imageurl = ''  # TODO: mettiamo un placeholder?

    descriptions = []
    for d in teacher.teacherdescription_set.all():
        descriptions.append(
            {"language": d.language,
             "label": d.label}
        )
    risposta = {
        "name": name,
        "imageUrl": imageurl,
        "desc": descriptions
    }
    return JsonResponse(risposta)


def user_courses(request, eco_user_id):
    risposta = []
    try:
        usa = get_object_or_404(UserSocialAuth, uid=eco_user_id)
    except Http404:
        return JsonResponse(risposta)
    # The pre-fetching of groups is done to make auth checks not require an
    # additional DB lookup (this kills the Progress page in particular).
    student = User.objects.prefetch_related("groups").get(id=usa.user.id)
    
    course_enrollements = student.courseenrollment_set.all()
    now = datetime.datetime.now(UTC())
    for ce in course_enrollements:
        course_key = ce.course_id
        course_key_str = u'%s' % course_key
        try:
            course = get_course_by_id(course_key)
        except Http404:
            # This souldn't be happen if course is delete correctly (deleting also enrollments)
            continue
        grade_summary = optimized_grade(student,request,course)  #grades.grade(student, request, course)

        modules = StudentModule.objects.filter(student=student, course_id=course_key)
        viewCount = modules.count()
        if viewCount > 0:
            firstViewDate = modules.order_by('created')[0].created.strftime("%Y-%m-%dT%H:%M:%S")
            lastViewDate = modules.order_by('-modified')[0].modified.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            firstViewDate = ""
            lastViewDate = ""

        # If cutoff is reached, and today > course.end_date -> course.end_date else ""
        nonzero_cutoffs = [cutoff for cutoff in course.grade_cutoffs.values() if cutoff > 0]
        success_cutoff = min(nonzero_cutoffs) if nonzero_cutoffs else None
        completedDate = ""
        if success_cutoff and grade_summary['percent'] > success_cutoff:
            if course.end < now:
                completedDate = course.end.strftime("%Y-%m-%dT%H:%M:%S")

        # Sum of difference between created and modified StudentModule for this course
        spentTime = timedelta()
        for m in modules:
            spentTime += m.modified - m.created
        spentTime = str(spentTime.seconds * 1000)  # Total time the user spent in this course in milliseconds

        risposta.append(
            {
                "id": course_key_str,  # it is a representation like u'edX/DemoX/Demo_Course'
                "viewCount": viewCount,
                "progressPercentage": grade_summary['percent'],
                # "currentPill": 3,  NOT USED because we provide progressPercentage
                "firstViewDate": firstViewDate,  # First StudentModule created
                "lastViewDate": lastViewDate,  # Last StudentModule modified
                "completedDate": completedDate,
                "spentTime": spentTime
            }
        )
    return JsonResponse(risposta)

def optimized_grade(student, request, course):
    '''
    Similar to instructor offline_gradecal.student_grades the offline_gradecalc but we need 
    to set a periodic task to update those data with a day(?) retention.
    Update need the django command compute_grades in background
    '''

    now = datetime.datetime.now(UTC())
    needRecalculation = False
    try:
        ocg = OfflineComputedGrade.objects.get(user=student, course_id=course.id)
        if (ocg.updated + datetime.timedelta(days=1)) < now :
            offline_calc.delay(course.id)
        return json.loads(ocg.gradeset)        
    except OfflineComputedGrade.DoesNotExist:
        grade_summary = dict(percent = 0 )  # assume this and run task for calculate
        offline_calc.delay(course.id)
        return grade_summary

