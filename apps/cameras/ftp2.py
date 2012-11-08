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

logging.basicConfig()
log = logging.getLogger("FTPServer")
hndlr = logging.handlers.RotatingFileHandler('/tmp/ftpserver.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hndlr.setFormatter(formatter)
log.addHandler(hndlr) 
log.setLevel(logging.INFO)
#log.setLevel('logging.WARN')
log.info("Starting the server")


connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')

#connect ('imagetest',host='ftp1.vid.ie', port =27017, username='imagetest', password = 'imagetest')

destinationdirectoryroot = '/images'

def upload(file, username):
    imgdir = ''
    try:
        log.info("starting Upload %s"%file)

        cams = Camera.objects.filter(name=username)
        c = cams[0]
        
        #thi is so that the files will be stored on s3 in the folder structure 
        #for the time it was uploaded for the camers's timezone.
        camtz = pytz.timezone(c.timezone) 
        utc = pytz.utc
        nowdt = datetime.datetime.utcnow() #get local datetime (no timezone data)
        utcnow = utc.localize(nowdt) #local datetime with timezone data
        nowdt = camtz.normalize(utcnow) #datetime at the camera's timezone

        #nowdt = datetime.datetime.utcnow()
        hm = nowdt.strftime('%H/%M')
        dt = nowdt.strftime('%Y%m%d')
 
        log.info( "writing:%s", file)

        key = '/%s/%s/%s/%s.jpg'%(dt,username,hm,uuid.uuid4())
        imgdir = '/%s/%s/%s/'%(dt,username,hm)
        c.latestimage= key
        c.save()    
        log.info( key)

        try:
            log.info("Thumbnail /thumbnail%s"%imgdir)
            os.makedirs("/thumbnail%s"%imgdir)
        except:
            pass
        log.info('after thumbnail dir')
        size = 128, 96
        im = PIL.open(file)
        im.thumbnail(size)
        im.save('/thumbnail%s'%key, "JPEG")
        log.info('after thumbnail save')
        
        i = Image(camera = cams[0], camname = cams[0].name, day = dt, hour = nowdt.strftime('%H'), minute = nowdt.strftime('%M'),  key=key, format = 'jpg')
        i.save()
        log.info( 'Saved image info to mongo with key %s'%key)
        try:
            ids = ImageData.objects.filter(camera = cams[0], year = nowdt.strftime('%Y'), month = nowdt.strftime('%m'), day = nowdt.strftime('%d'), hour = nowdt.strftime('%H'))
            id = ids[0]
            id.counts = id.counts +1
            id.save()
        except:
            id = ImageData(camera = cams[0], year = nowdt.strftime('%Y'), month = nowdt.strftime('%m'), day = nowdt.strftime('%d'), hour = nowdt.strftime('%H'), counts=1)
            id.save()

        log.info( 'Saved image data to mongo with key %s'%key)
        
    except Exception, ex:
        log.error( "Error while saving file %s"%file)
        log.error( ex)
    
    try:
        try:
            os.makedirs("%s%s"%(destinationdirectoryroot,imgdir))
        except:
            pass
        os.rename(file, '%s%s'%(destinationdirectoryroot,key))
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
        log.info("Handler User Login START %s" %username)
        try:
            #connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')
            cams = Camera.objects.filter(name=username)
            c =  cams[0]
            
            c.currentipaddress = self.remote_ip
            c.save()
        except:
            pass
        log.info("Handler User Login END %s" %username)
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass
        
    def on_file_sent(self, file):
        log.info( 'File Sent %s'% file)
        pass

    def on_file_received(self, file):
        try:
            log.info("Handler File received %s" %file)
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


class SimpleDBOperations(object):
    '''Storing connection object'''
    def __init__(self):
        self.perm = None
        self.username = None
        self.path = None

    def authenticate(self, username, password):
        log.debug( 'authenticate "%s" "%s"'%(username, password))
        log.info("Authenticate %s" %username)
        self.username = username
        self.password = password
        
        
        authenticated = False
        try:
            #connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')
            cams = Camera.objects.filter(name=username, password=password)
            if len(cams) > 0:
                authenticated = True
                self.path = cams[0].path
                self.perm = cams[0].path
                try:
                    log.debug( 'Trying to create "%s" '%(self.path))
                    #subprocess.call(["mkdir", "-p", self.path])
                    
                    os.makedirs(self.path)
                except Exception, ex:
                    log.debug(ex)
            else:
                log.debug('authenticate failed %s %s'%(username, password))
                    
        except Exception, ex:
            log.error(ex)
            log.error("error authenticating %s"%username)

        log.debug( 'authenticate finish %s'%(username))
        if authenticated:
            return True
        else:
            return False
        


    def __repr__(self):
        return self.connection

operations = SimpleDBOperations()


class SimpleDBAuthorizer(ftpserver.DummyAuthorizer):
    '''FTP server authorizer. Logs the users into Putio Cloud
Files and keeps track of them.
'''
    users = {}

    def validate_authentication(self, username, password):
        log.debug( 'validate_authentication %s' %username)
        try:
            return operations.authenticate(username, password)
        except:
            return False

    def has_user(self, username):
        return username != 'anonymous'

    def has_perm(self, username, perm, path=None):

        log.debug( 'has_perm')
        log.debug( 'calling has perm %s %s'%( perm, path))
        log.debug( 'homedir %s' % operations.path)
        
        if path.find( operations.path) == 0:
          
            log.debug( 'Has perm %s %s ' %( perm, path))
            return True
        else:
        
            log.debug( 'No perm %s %s ' %( perm, path))
            return False
        
    def override_perm(self, username, directory, perm, recursive=False):
        """Override permissions for a given directory."""
        log.debug( 'override %s %s %s '%( username, directory, perm))
  
    def get_perms(self, username):
        return operations.perm

    def get_home_dir(self, username):
        log.debug( 'calling get_home_dir')
        try:
            log.debug( 'make %s'%operations.path)
            os.makedirs(operations.path)
        except Exception, ex:
            log.debug( ex)
            pass        
        if not os.path.isdir(operations.path):
            raise ValueError('no such directory: "%s"' % operations.path)
        
        homedir = os.path.realpath(operations.path)
        return homedir


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
handler.authorizer = authorizer
if env == 'PROD':
    logging.info('Environment In production %s'%env)
#    handler.passive_ports =range(1024,1048)
#    handler.masquerade_address = '174.129.164.207'
else:
    pass
address = ("0.0.0.0", 21)
ftpd = ftpserver.FTPServer(address, handler)

ftpd.serve_forever()
