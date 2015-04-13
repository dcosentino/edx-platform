
from celery.task import task
from instructor.offline_gradecalc import student_grades , offline_grade_calculation 

@task()
def offline_calc(course):
    log.info("Start task celery for offline_calc for "+course.id)
    offline_grade_calculation(course.id)
