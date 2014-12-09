#-*- coding: utf-8 -*-

from django.db import models

LINGUE = (
    ('en', 'English'),
    ('it', 'Italiano'),
)

class Teacher(models.Model):
    first_name = models.CharField(max_lenght=64)
    last_name = models.CharField(max_lenght=64)

class Description(models.Model):
    language = models.CharField(max_length=2, choices="LINGUE")
    label = models.TextField()

    
