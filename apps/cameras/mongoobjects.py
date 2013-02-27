
from mongoengine import *

import datetime


class User(Document):
    email = StringField(required=True)
    name = StringField(required=True)
    password = StringField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.utcnow)

class Camera(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    description = StringField(required=True)
    owner = ReferenceField(User)
    created = DateTimeField(required=True, default=datetime.datetime.utcnow)
    path = StringField(required=True, unique=True)
    perm = StringField(required=True)
    latestimage = StringField(required=False)
    currentipaddress = StringField(required=False)
    publickey = StringField(required=False)
    publicdescription = StringField(required=False)
    timezone =  StringField(required=False)
    filter  =  StringField(required=False)
    meta = {
        'ordering': ['-created']
    }
#'ordering': ['+name']
class Image(Document):
    camera = ReferenceField(Camera)
    camname = StringField(required=True)
    key = StringField(required=True)
    format = StringField(required=True)
    day = IntField(required=True)
    hour = IntField(required=True)
    minute = IntField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.utcnow)
    meta = {
        'ordering': ['+created']
    }


class ImageData(Document):
    camera = ReferenceField(Camera)
    year = IntField(required=True)
    month = IntField(required=True)
    day = IntField(required=True)
    hour = IntField(required=True)
    counts = IntField(required=True)
    meta = {
        'ordering': ['+year', '+month', '+day', '+hour']
    }
