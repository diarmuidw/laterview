'''
Created on 18 Nov 2011

@author: bluekulu
'''
from pyftpdlib import ftpserver

from mongoengine import connect

import datetime, pytz, uuid, subprocess, os

import logging

import logging.handlers

from mongoobjects  import Image, Camera, ImageData

import uuid

import Image as PIL


import local_settings 

import urllib

import hoover

import redis
import string
from filter import Filter, FilterManager
import numpy
import scipy

logging.basicConfig()
log = logging.getLogger("FTPServer")
hndlr = logging.handlers.RotatingFileHandler('/tmp/ftpserver.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hndlr.setFormatter(formatter)
log.addHandler(hndlr) 
log.setLevel(logging.DEBUG)
handler = hoover.LogglyHttpHandler(token='43503870-6508-4c7c-9e98-2ca79f5d4d2c')

log.addHandler(handler)

log.info ("Starting the ftp server")

connect ('imagetest',host=local_settings.HOST, port =local_settings.PORT, username=local_settings.USER, password = local_settings.PASSWORD)

destinationdirectoryroot = '/images' #no trailing slash

import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def getipaddress():
    
    # Get a file-like object for the Python Web site's home page.
    f = urllib.urlopen(local_settings.IPSERVER)
    # Read from the object, storing the page's contents in 's'.
    s = f.read()
    f.close()
    s = s.rstrip()
    return s

def upload(file, username):
    imgdir = ''
    try:
        log.info ("starting Upload %s"%file)

        cams = Camera.objects.filter(name=username)
        c = cams[0]
        
        #this is so that the files will be stored on s3 in the folder structure 
        #for the time it was uploaded for the camers's timezone.
        camtz = pytz.timezone(c.timezone) 
        utc = pytz.utc
        nowdt = datetime.datetime.utcnow() #get local datetime (no timezone data)
        utcnow = utc.localize(nowdt) #local datetime with timezone data
        nowdt = camtz.normalize(utcnow) #datetime at the camera's timezone

        #nowdt = datetime.datetime.utcnow()
        hm = nowdt.strftime('%H/%M')
        dt = nowdt.strftime('%Y%m%d')
 
        log.debug( "writing:%s", file)

        key = '/%s/%s/%s/%s.jpg'%(dt,username,hm,uuid.uuid4())
        imgdir = '/%s/%s/%s/'%(dt,username,hm)
        c.latestimage= key
        c.save()    
        log.debug( key)
        if local_settings.DOTHUMBNAIL:
            try:
                log.debug("Thumbnail /thumbnail%s"%imgdir)
                os.makedirs("/thumbnail%s"%imgdir)
            except:
                pass
            log.debug('after thumbnail dir')
            size = 128, 96
            im = PIL.open(file)
            im.thumbnail(size)
            im.save('/thumbnail%s'%key, "JPEG")
            log.debug('after thumbnail save')
        
        i = Image(camera = cams[0], camname = cams[0].name, day = dt, hour = nowdt.strftime('%H'), minute = nowdt.strftime('%M'),  key=key, format = 'jpg')
        i.save()
        log.debug( 'Saving image info to mongo with key %s'%key)
        try:
            ids = ImageData.objects.filter(camera = cams[0], year = nowdt.strftime('%Y'), month = nowdt.strftime('%m'), day = nowdt.strftime('%d'), hour = nowdt.strftime('%H'))
            id = ids[0]
            id.counts = id.counts +1
            id.save()
        except:
            id = ImageData(camera = cams[0], year = nowdt.strftime('%Y'), month = nowdt.strftime('%m'), day = nowdt.strftime('%d'), hour = nowdt.strftime('%H'), counts=1)
            id.save()
        try:
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            r.incr("allimages")
            r.incr("%s~%s~%s"%( nowdt.strftime('%Y'), nowdt.strftime('%m'), nowdt.strftime('%d'))) 
            r.incr(username)
            r.incr("%s~%s~%s~%s~%s"%(username, nowdt.strftime('%Y'), nowdt.strftime('%m'), nowdt.strftime('%d'),  nowdt.strftime('%H')))
            r.incr("%s~%s~%s~%s"%(username, nowdt.strftime('%Y'), nowdt.strftime('%m'), nowdt.strftime('%d')))
            r.incr("%s~%s~%s"%(username, nowdt.strftime('%Y'), nowdt.strftime('%m')))
            
        except Exception, ex:
            log.debug(ex)
            log.debug("Error doing upload redis save")

        log.info ( 'Saved image data to mongo with key %s'%key)
        
    except Exception, ex:
        log.error( "Error while saving file %s"%file)
        log.error( ex)
    
    try:
        try:
            os.makedirs("%s%s"%(destinationdirectoryroot,imgdir))
        except:
            pass
        img_filter = Filter(local_settings.FILTER, 'crgb')
        im = PIL.open(file)
        
        im.show()

        image_array = numpy.array(im)

        filter_manager = FilterManager()
        filter_manager.add_filter(img_filter)

        filter_array = filter_manager.apply_filter('crgb', image_array)
        im = PIL.fromarray(filter_array)
        name = id_generator(6)
        im.save('/tmp/%s.jpg'%name)
        log.debug( '/tmp/%s.jpg'%name)
        os.rename('/tmp/%s.jpg'%name, '%s%s'%(destinationdirectoryroot,key))


    except Exception, ex:
        log.error(ex)
        log.error("Error while saving file %s to %s"%(file, key))
                  
    try:
        os.remove(file)
    except:
        pass
    pass                 
       





class MyHandler(ftpserver.FTPHandler):

    def on_login(self, username):
        # do something when user login
        log.debug("Handler User Login START %s" %username)
        try:
            #connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')
            cams = Camera.objects.filter(name=username)
            c =  cams[0]
            
            c.currentipaddress = self.remote_ip
            c.save()
        except:
            pass
        log.debug("Handler User Login END %s" %username)
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass
        
    def on_file_sent(self, file):
        log.debug( 'File Sent %s'% file)
        pass

    def on_file_received(self, file):
        try:
            log.debug("Handler File received %s" %file)
            #pile.spawn(upload, file)
            upload(file, self.username)
             
        except Exception, ex:
            log.error( ex)
            log.error('error on_file_received %s'%file)
            
    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        
        os.remove(file)



class SimpleDBAuthorizer(ftpserver.DummyAuthorizer):
    '''FTP server authorizer. Logs the users into Putio Cloud
Files and keeps track of them.
'''
    read_perms = "elr"
    write_perms = "adfmwM"

    def __init__(self):
        self.user_table = {}

    def add_user(self, username, password, homedir, perm='elr',
                    msg_login="Login successful.", msg_quit="Goodbye."):
        """Add a user to the virtual users table.

        AuthorizerError exceptions raised on error conditions such as
        invalid permissions, missing home directory or duplicate usernames.

        Optional perm argument is a string referencing the user's
        permissions explained below:

        Read permissions:
         - "e" = change directory (CWD command)
         - "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
         - "r" = retrieve file from the server (RETR command)

        Write permissions:
         - "a" = append data to an existing file (APPE command)
         - "d" = delete file or directory (DELE, RMD commands)
         - "f" = rename file or directory (RNFR, RNTO commands)
         - "m" = create directory (MKD command)
         - "w" = store a file to the server (STOR, STOU commands)
         - "M" = change file mode (SITE CHMOD command)

        Optional msg_login and msg_quit arguments can be specified to
        provide customized response strings when user log-in and quit.
        """
        log.debug('adding user %r' % username)
        try:
            value = self.user_table[username]
            log.debug('allready exists user %r' % username)
        except KeyError:
            # Key is not present
            
        
            homedir = os.path.realpath(homedir)
            #self._check_permissions(username, perm)
            dic = {'pwd': str(password),
                   'home': homedir,
                   'perm': perm,
                   'operms': {},
                   'msg_login': str(msg_login),
                   'msg_quit': str(msg_quit)
                   }
            self.user_table[username] = dic    
        log.debug('finished adding user %r' % username)
     
    
    def authenticate(self, username, password):
        log.debug( 'authenticate "%s" "%s"'%(username, password))
        log.debug("Authenticate %s" %username)

        authenticated = False
        try:
            #connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')
            cams = Camera.objects.filter(name=username, password=password)
            if len(cams) > 0:
                authenticated = True
                path = cams[0].path
                perm = cams[0].perm
                try:
                    log.debug( 'Trying to create "%s" '%(path))
                    #subprocess.call(["mkdir", "-p", self.path])
                    
                    os.makedirs(path)
                except Exception, ex:
                    log.debug(ex)
            else:
                log.debug('authenticate failed %s %s'%(username, password))
                    
        except Exception, ex:
            log.error(ex)
            log.error("error authenticating %s"%username)

        log.debug( 'authenticate finish %s'%(username))
        if authenticated:
            try:
                log.debug("adding user " + username)
                SimpleDBAuthorizer.add_user(self, username, password, path, perm)
            except Exception, ex:
                log.error( ex)
            return True
        else:
            return False
    
    def validate_authentication(self, username, password):
        log.debug( 'validate_authentication %s' %username)
        try:
            return SimpleDBAuthorizer.authenticate(self, username, password)
        except Exception, ex:
            log.debug (ex)
            return False

    def has_user(self, username):
        try:
            value = self.user_table[username]
            return True
        except KeyError:
            # Key is not present
            return False
        

    def has_perm(self, username, perm, path=None):
        try:
            log.debug( 'has_perm')
            log.debug( 'calling has perm %s %s'%( perm, path))
            
            log.debug (self.user_table[username]['perm'])

        except Exception, ex:
            log.debug(ex)
        return True
        
    
        
    def override_perm(self, username, directory, perm, recursive=False):
        """Override permissions for a given directory."""
        log.debug( 'override %s %s %s '%( username, directory, perm))
  
    def get_perms(self, username):
        return self.user_table[username]['perm']

    def get_home_dir(self, username):
        log.debug( 'calling get_home_dir')
#        try:
#            log.debug( 'make %s'%operations.path)
#            os.makedirs(operations.path)
#        except Exception, ex:
#            log.debug( ex)
#            pass        
#        if not os.path.isdir(operations.path):
#            raise ValueError('no such directory: "%s"' % operations.path)
#        
#        homedir = os.path.realpath(operations.path)
#        return self.user_table[username]['home']
        path = "/tmp/images/%s"%username
        try:
            log.debug( 'Trying to create "%s" '%(path))
            os.makedirs(path)
        except Exception, ex:
            log.debug(ex)
        return "/tmp/images/%s"%username
      


    def get_msg_login(self, username):
        return 'Welcome %s' % username

    def get_msg_quit(self, username):
        return 'Goodbye %s' % username
        
        
from configobj import ConfigObj
config = ConfigObj('ftp.ini')
env = config['ENV']
logging.info('Environment %s'%env)

authorizer = SimpleDBAuthorizer()

handler = MyHandler
#del handler.proto_cmds['PASV']
#del handler.proto_cmds['EPSV']
handler.authorizer = authorizer
if env == 'PROD':
    logging.info('Environment In production %s'%env)
    portstart = int( local_settings.PORTSTART)
    portend = int( local_settings.PORTEND)
    handler.passive_ports =range(portstart,portend)
    log.debug (getipaddress())
    handler.masquerade_address = getipaddress()
else:
    pass
address = ("0.0.0.0", 21)
ftpd = ftpserver.FTPServer(address, handler)

ftpd.serve_forever()








