#!/usr/bin/env python

from MultiUpload import MultiUpload

from mediaExchange.movies.models import Item, UploadRequest, DownloadFile
from mediaExchange.poster.encode import multipart_encode
from mediaExchange.poster.streaminghttp import register_openers

#import ftplib
import hashlib
import math
import os
import re
import rsa
from rsa.bigfile import encrypt_bigfile
import sys
import tarfile
import threading
import time
import traceback
import urllib2
from Crypto.Cipher import Blowfish


STATE_QUEUED = 0
STATE_TARING = 1
STATE_ENCRYPTING = 2
STATE_SPLITTING = 3
STATE_UPLOADING = 4

MAX_FILE_SIZE = 1000000000
ENCRYPTION_KEY = 'thisistheencryptionkey1234567890!"$%&/()=?+*#,.-;:_>.<'
ENCRYPTION_CHUNK_SIZE = 100000000
DOWNLOAD_PASSWORD = 'thisisthedownloadpassword'
MIN_NICE_LEVEL = 15
PRIVATE_KEY = "/tmp/privKey.pem"
PUBLIC_KEY = "/tmp/pubKey.pem"

DONE = False

def main():
    renice()
    while not DONE:
#        ur = UploadRequest.objects.filter(done = False, tries__in=range(3)).order_by('id')
        ur = UploadRequest.objects.filter(done = False).order_by('id')
        if ur:
            ur = ur[0]
            ur.tries += 1
            ur.save()
            print 'processing', ur
            pack(ur.item, ur)
            if DownloadFile.objects.filter(item=ur.item):
                ur.done = True
                ur.save()
        else:
            time.sleep(10)

def renice():
    nice = os.nice(0)
    if nice < MIN_NICE_LEVEL:
        nice = os.nice(MIN_NICE_LEVEL-nice)
        assert nice == MIN_NICE_LEVEL

def pack(item, uploadRequest):
    print 'pack(', item, ',', uploadRequest,')'
    encfiles = []
    taredFile = None
    encfile = None
    try:
        uploadRequest.state=STATE_TARING
        uploadRequest.save()
        taredFile = tarDownload(item.path)
        uploadRequest.state=STATE_ENCRYPTING
        uploadRequest.save()
        encfile = encryptDownloadRSA(uploadRequest, taredFile)
        uploadRequest.state=STATE_SPLITTING
        uploadRequest.save()
        encfiles = splitFile(uploadRequest, encfile)
        uploadRequest.state=STATE_UPLOADING
        uploadRequest.save()
        upload(uploadRequest=uploadRequest, files=encfiles)
    except KeyboardInterrupt, e:
        uploadRequest.state=STATE_QUEUED
        uploadRequest.save()
        deletefiles = []
        if taredFile:
            deletefiles.append(taredFile)
            if encfile:
                deletefiles.append(encfile)
                if encfiles:
                    deletefiles += encfiles
        cleanup(deletefiles)
        print 'GOODBYE'
        sys.exit(0)
    except:
        print 'ERROR: upload failed:'
        print traceback.print_exc()
    uploadRequest.state=STATE_QUEUED
    uploadRequest.save()
    deletefiles = []
    if taredFile:
        deletefiles.append(taredFile)
        if encfile:
            deletefiles.append(encfile)
            if encfiles:
                deletefiles += encfiles
    cleanup(deletefiles)

def upload(uploadRequest, files):
    print 'upload(', uploadRequest,',', files, ')'
    for file in files:
        uploadFile(uploadRequest, file)

def tarDownload(file):
    print 'tarDownload(', file,')'
    tmpfile = '/tmp/%s.tar' % (os.path.basename(file))
    tar = tarfile.open(tmpfile, 'w')
    tar.add(file)
    tar.close()
    return tmpfile

def encryptDownload(uploadRequest, file):
    print 'encryptDownload(',file,')'
    tmpfile = '/tmp/%s' % (hashlib.sha1(file).hexdigest())
    blowfish = Blowfish.new(key=ENCRYPTION_KEY)
    dfh = open(tmpfile, 'wb')
    sfh = open(file, 'rb')
    sfsize = os.stat(file).st_size
    parts = int(math.ceil(float(sfsize)/float(ENCRYPTION_CHUNK_SIZE)))
    for i in range(parts):
        dfh.write(blowfish.encrypt(sfh.read(ENCRYPTION_CHUNK_SIZE)))
        percent = int((i+1)/float(parts)*100.0)
#        print percent
        uploadRequest.encrypted = percent
        uploadRequest.save()
    dfh.close()
    sfh.close()
    return tmpfile

def encryptDownloadRSA(uploadRequest, file):
    print "encryptDownloadRSA(", file, ")"
    pubKey = rsa.PublicKey.load_pkcs1(open(PUBLIC_KEY).read())
    tmpfile = '/tmp/%s' % (hashlib.sha1(file).hexdigest())
    dfh = open(tmpfile, 'wb')
    sfh = open(file, 'rb')
    encrypt_bigfile(sfh, dfh, pubKey)
    dfh.close()
    sfh.close()
    uploadRequest.encrypted = 100
    uploadRequest.save()
    return tmpfile

def splitFile(uploadRequest, file):
    'splitFile(',file,')'
    result = [file]
    filesize = os.stat(file).st_size
    print file, 'has size:', filesize
    if filesize > MultiUpload.MAX_FILESIZE:
        print 'Creating multiple files.'
        result = []
        parts = int(math.ceil(float(filesize) / float(MultiUpload.MAX_FILESIZE)))
        sfh = open(file, 'rb')
        for part in range(parts):
            tmpfile = file+str(part)
            print 'packing part', part, 'filename:', tmpfile
            dfh = open(tmpfile, 'wb')
            for i in range(1000):
                dfh.write(sfh.read(int(math.ceil(float(MultiUpload.MAX_FILESIZE)/float(1000)))))
                percent = int((part+1)*(float(i+1)/1000.0)/parts*100)
                uploadRequest.splitted = percent
                uploadRequest.save()
            dfh.close()
            result.append(tmpfile)
    return result
    
def uploadFile(uploadRequest, file):
    mu = MultiUpload()
    mu.uploadData(file, uploadRequest)
#    uploadFilebase(uploadRequest, file, item)

#def ftpUploadFilebase(file):
#    basename = os.path.basename(file)
#    ftp = ftplib.FTP('ftp.filebase.to')
#    ftp.login('21050', '1bf5890f69200')
#    ftp.storbinary('STOR %s' % (basename), open(file, 'rb'))
#
#def uploadFilebase(uploadRequest, file, item):
#    regex = re.compile(re.escape('<h4><a href="') + '(.*?)' + re.escape('" target="_blank">'), re.M | re.S | re.I)
#    credentials = getFilebase()
#    if credentials:
#        # Register the streaming http handlers with urllib2
#        register_openers()
#
#        fileHandle = open(file)
#
#        # Start the multipart/form-data encoding of the file "DSC0001.jpg"
#        # "image1" is the name of the parameter, which is normally set
#        # via the "name" parameter of the HTML <input> tag.
#
#        # headers contains the necessary Content-Type and Content-Length
#        # datagen is a generator object that yields the encoded parameters
#        datagen, headers = multipart_encode(
#            {
#                'upload_type' : '1',
#                'UPLOAD_IDENTIFIER' : credentials['upload_id'],
#                'user_id' : credentials['user_id'],
#                'fb_nickname' : credentials['nickname'],
#                'fb_passwort' : credentials['password'],
#                'anz_files' : '1',
#                'file_1' : fileHandle,
#                'urlbox' : '',
#                'description' : '',
#                'passwort' : DOWNLOAD_PASSWORD,
#                'server' : credentials['server'],
#                'submit' : 'Datei hochladen',
#            })
#        headers.update({'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.10) Gecko/2009042523 Ubuntu/9.04 (jaunty) Firefox/3.0.10'})
##        print datagen
##        print headers
#
#        # Start a thread that checks how much is being uploaded.
#        t = threading.Thread(target=updateUploadState, args=(uploadRequest, fileHandle, os.stat(file).st_size))
#        t.start()
#
#        # Create the Request object
#        request = urllib2.Request(credentials['url'], datagen, headers)
#        # Actually do the request, and get the response
#        source = urllib2.urlopen(request).read()
#
#        match = regex.search(source)
#        if match:
#            df = DownloadFile(item=item, downloadLink=match.group(1))
#            df.save()
#        else:
#            print "ERROR: cannot fetch download link for filebase"
#
#def updateUploadState(uploadRequest, filehandle, totalsize):
#    print 'updateUploadState(', uploadRequest, ',', filehandle, ',', totalsize, ')'
#    done = False
#    uploadRequest.state = STATE_UPLOADING
#    while not done:
#        time.sleep(10)
#        cur = filehandle.tell()
#        percent = int((cur+1)/float(totalsize)*100)
##        print percent
#        uploadRequest.uploaded = percent
#        uploadRequest.save()
#        if totalsize == cur:
#            filehandle.close()
#            done = True


#def getFilebase():
#    result = None
#    regex_string = re.escape('<form action="') + \
#        '(.*?)' + \
#        re.escape('" enctype="multipart/form-data" method="post" name="upload" id="upload" onsubmit="InitUploadStatus();">') + \
#        '.*?' + \
#        re.escape('<input type="hidden" name="UPLOAD_IDENTIFIER" id="upload_identifier" value="') + \
#        '(.*?)' + \
#        re.escape('"') + \
#        '.*?' + \
#        re.escape('<input type="hidden" name="server" value="') + \
#        '(.*?)' + \
#        re.escape('"')
##    print 'regex_string:', regex_string
#    regex = re.compile(regex_string, re.M | re.I | re.S)
#    source = urllib2.urlopen('http://filebase.to/index.php').read()
##    print 'SOURCE:\n\n\n\n\n', source, '\n\n\n\n\n'
#    match = regex.search(source)
#    if match:
#        result = {'url' : match.group(1), 'upload_id' : match.group(2), 'user_id' : '21050', 'nickname' : 'nookieman', 'password' : 'e98df890da55378cfa89ff7907f75db2', 'server' : match.group(3)}
#        print 'filebase credentials:', result
#    else:
#        print "ERROR: cannot parse filebase upload fields"
#    return result

def cleanup(filelist):
    print 'cleanup(%s) called' % (str(filelist))
    for file in filelist:
        if os.path.isfile(file):
            os.remove(file)



if __name__ == '__main__':
    main()
