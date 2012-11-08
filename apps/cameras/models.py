
from django.db import models


#class Post(models.Model):
#    title = models.CharField()
#    text = models.TextField()
#    tags = ListField()
#    comments = ListField()
#
#
#class User(models.Model):
#    email = models.CharField()
#    name = models.TextField()
#    password = models.CharField()
#    created = models.DateTimeField(default = datetime.datetime.now())
#
#
#class Camera(models.Model):
#    name = models.CharField()
#    password = models.CharField()
#    owner = models.ForeignKey(User)
#    path = models.CharField()
#    perm = models.CharField()
#    created = models.DateTimeField(default = datetime.datetime.now())
#
#class Image(models.Model):
#    camera = models.ForeignKey(Camera)
#    camname = models.CharField()
#    key = models.CharField()
#    format = models.CharField()
#    created = models.DateTimeField(default = datetime.datetime.now())
