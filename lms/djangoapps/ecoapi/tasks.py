
from celery.task import task
from instructor.offline_gradecalc import student_grades , offline_grade_calculation 

#TODO: add a better task management to prevent concurrent task execution with some course_id

@task()
def offline_calc(course_id):
    offline_grade_calculation(course_id)
