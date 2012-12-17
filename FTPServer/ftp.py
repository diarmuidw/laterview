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


logging.basicConfig()
log = logging.getLogger("FTPServer")
hndlr = logging.handlers.RotatingFileHandler('/tmp/ftpserver.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hndlr.setFormatter(formatter)
log.addHandler(hndlr) 
log.setLevel(logging.DEBUG)
#log.setLevel('logging.WARN')
log.info("Starting the server")


connect ('imagetest',host=local_settings.HOST, port =local_settings.PORT, username=local_settings.USER, password = local_settings.PASSWORD)

#connect ('imagetest',host='ftp1.vid.ie', port =27017, username='imagetest', password = 'imagetest')

destinationdirectoryroot = '/images' #no trailing slash


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
        if local_settings.DOTHUMBNAIL:
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
        log.info( 'Saving image info to mongo with key %s'%key)
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


#class SimpleDBOperations(object):
#    '''Storing connection object'''
#    def __init__(self):
#        self.perm = None
#        self.username = None
#        self.path = None
#
#    def authenticate(self, username, password):
#        log.debug( 'authenticate "%s" "%s"'%(username, password))
#        log.info("Authenticate %s" %username)
#        self.username = username
#        self.password = password
#        
#        
#        authenticated = False
#        try:
#            #connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')
#            cams = Camera.objects.filter(name=username, password=password)
#            if len(cams) > 0:
#                authenticated = True
#                self.path = cams[0].path
#                self.perm = cams[0].path
#                try:
#                    log.debug( 'Trying to create "%s" '%(self.path))
#                    #subprocess.call(["mkdir", "-p", self.path])
#                    
#                    os.makedirs(self.path)
#                except Exception, ex:
#                    log.debug(ex)
#            else:
#                log.debug('authenticate failed %s %s'%(username, password))
#                    
#        except Exception, ex:
#            log.error(ex)
#            log.error("error authenticating %s"%username)
#
#        log.debug( 'authenticate finish %s'%(username))
#        if authenticated:
#            return True
#        else:
#            return False
#        
#
#
#    def __repr__(self):
#        return self.connection
#
#operations = SimpleDBOperations()


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
        log.info("Authenticate %s" %username)

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
            print ex
            return False

    def has_user(self, username):
        try:
            value = self.user_table[username]
            return True
        except KeyError:
            # Key is not present
            return False
        

    def has_perm(self, username, perm, path=None):

        log.debug( 'has_perm')
        log.debug( 'calling has perm %s %s'%( perm, path))
        
        
        if path is None:
            return perm in self.user_table[username]['perm']

        path = os.path.normcase(path)
        print(self.user_table)
        return perm in self.user_table[username]['perm']


        
#        if path.find( operations.path) == 0:
#          
#            log.debug( 'Has perm %s %s ' %( perm, path))
#            return True
#        else:
#        
#            log.debug( 'No perm %s %s ' %( perm, path))
#            return False
        
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
        #return self.user_table[username]['home']
        return "/tmp"


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
    print getipaddress()
    handler.masquerade_address = getipaddress()
else:
    pass
address = ("0.0.0.0", 21)
ftpd = ftpserver.FTPServer(address, handler)

ftpd.serve_forever()




