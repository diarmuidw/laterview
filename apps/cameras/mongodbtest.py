
from mongoengine import *

import datetime

connect ('imagetest',host='ds029217.mongolab.com', port =29217, username='roletest', password = 'roletestpassw0rd')


from mongoobjects  import *


#u = User(email = 'admin@aaa.com', name = 'cam001', password = '12345')
#u.save()
#u = User(email = 'admin@aaa.com', name = 'cam003', password = '12345')
#u.save()
#c = Camera(name = 'cam001', password = 'password', path = '/tmp/t1/t2/t4/cam001/', perm = 'elradfmw'  )

#c.save()
#c = Camera(owner = u, name = 'cam003', password = 'password', path = '/tmp/t1/t2/t4/cam003/', perm = 'elradfmw'  )
#c.save()
#
#i = Image(camera = c,camname = c.name,  key='12345', format = 'jpg')
#i.save()
#
#users = User.objects()
#print users
#for u in users:
#    print u.email
#    #c = Camera(owner = u, name = 'cam001', password = 'password', path = '/tmp/t1/t2/t4/cam001/', perm = 'elradfmw'  )
#    #c.save()
#    #cams = Camera.objects.filter(name='cam001')
#    #c = cams[0]
#    #c.owner = u
#    #c.save()
#    cams = Camera.objects.filter(owner = u)
#    print cams
#    for c in cams:
#        print c.name
#        images = Image.objects.filter(camname = c.name)
#        for i in images:
#            print i.key
#            data = i.key.split('/')
#            print data[0], data[2], data[3]
#            i.date = data[0]
#            i.hour = data[2]
#            i.minute = data[3]
#            i.save()
startday = 20120216

#images = Image.objects.all()
#for i in images:
#    k = i.key
#    print i.key
#    data = i.key.split('/')
#    
#    i.day = data[0]
#    i.hour = data[2]
#    i.minute = data[3]
#    i.save()
#    
#    ri = Image.objects.filter(key=k)
#    j = ri[0]
#    print 'retrieved', j.day, j.hour, j.minute

#
#cams = Camera.objects.all()
##
##for c in cams:
##    currentday = startday
##    while currentday < 20120217:
##        for h in range(0,24):
##            images = Image.objects.filter(camname = c.name, day = currentday, hour = h)
##            print c.name, currentday, h, len(images)
##            if len(images) > 0:
##                id = ImageData(camera = c, year = 2012, month = 2, day = currentday - 20120200, hour = h, counts=len(images))
##                id.save()
##                print id
##            
##        currentday = currentday +1
##        
##cams = Camera.objects.all()
#
#for c in cams:
#    currentday = startday
#
#    while currentday < 20120218:
#        for h in range(0,24):
#            images = Image.objects.filter(camname = c.name, day = currentday, hour = h)
#            print c.name, currentday, h, len(images)
#            if len(images) > 0:
#                id = ImageData(camera = c, year = 2012, month = 2, day = currentday - 20120200, hour = h, counts=len(images))
#                id.save()
#                print id
#            
#        currentday = currentday +1       



cams = Camera.objects.filter(name = 'cam001')
print cams
        #print 'should return a camera'
        #print cams[0].path, cams[0].perm
nowdt = datetime.datetime.now()
hm = nowdt.strftime('%H/%M')
dt = nowdt.strftime('%Y%m%d')
try:
    ids = ImageData.objects.filter(camera = cams[0], year = nowdt.strftime('%Y'), month = nowdt.strftime('%m'), day = nowdt.strftime('%d'), hour = nowdt.strftime('%H'))
    id = ids[0]
    print id.counts
    id.counts = id.counts +1
    id.save()
except Exception, ex:
    print 'no data'
#    
    id = ImageData(camera = cams[0], year = nowdt.strftime('%Y'), month = nowdt.strftime('%m'), day = nowdt.strftime('%d'), hour = nowdt.strftime('%H'), counts=1)
    id.save()

#print 'aaaaaaaaaaaaaaaaaaaaaaaaaa'
#images = Image.objects()
#for i in images:
#    print i.key, i.camname
#authenticate

cams = Camera.objects.filter(name='cam001', password='password')
print 'should return a camera'
print cams[0].path, cams[0].perm

cams = Camera.objects.filter(name='cam001', password='wrongpassword')
print cams

