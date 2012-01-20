#!/usr/bin/env python

from MultiUpload import MultiUpload
from uploader import *

from mediaExchange.movies.models import UploadRequest, DownloadFile, DownloadFileGroup, EncryptionKey

from mediaExchange.settings import ENCRYPTION_KEY, ENCRYPTION_CHUNK_SIZE

import os
import sys
import time
import traceback
from Crypto.Cipher import Blowfish


STATE_QUEUED = 0
STATE_TARING = 1
STATE_ENCRYPTING = 2
STATE_SPLITTING = 3
STATE_UPLOADING = 4

MIN_NICE_LEVEL = 15

DONE = False

def main():
    renice(MIN_NICE_LEVEL)
    while not DONE:
        ur = selectUploadRequest()
        if ur:
            ur.tries += 1
            ur.save()
            print 'processing', ur
            pack(ur)
            if DownloadFileGroup.objects.filter(itemInstance=ur.itemInstance):
                ur.done = True
                ur.save()
        else:
            time.sleep(10)

def selectUploadRequest():
    ur = None
    for uploadRequest in UploadRequest.objects.filter(done = False).order_by('id'):
        if os.path.exists(uploadRequest.itemInstance.path):
            ur = uploadRequest
            break
        else:
            print "WARNING: item path does not exist: '%s'" % uploadRequest.itemInstance.path
    return ur

def pack(uploadRequest):
    print 'pack', (uploadRequest,)
    chunkSize = ENCRYPTION_CHUNK_SIZE
    keyData = ENCRYPTION_KEY
    encfiles = []
    taredFile = None
    encfile = None
    try:
        uploadRequest.state=STATE_TARING
        uploadRequest.save()

        taredFile = tarFiles([uploadRequest.itemInstance.path])

        uploadRequest.state=STATE_ENCRYPTING
        uploadRequest.save()

        hashname = createHash([uploadRequest.itemInstance.path])
        encfile = encryptFile(taredFile, hashname, chunkSize, keyData, uploadRequest)

        uploadRequest.state=STATE_SPLITTING
        uploadRequest.save()

        mu = MultiUpload()
        encfiles = splitFile(encfile, mu.MAX_FILESIZE, uploadRequest)

        uploadRequest.state=STATE_UPLOADING
        uploadRequest.save()

        linkList = uploadFiles(uploadRequest=uploadRequest, fileHoster=mu, files=encfiles)
        storeLinks(linkList, uploadRequest.itemInstance, chunkSize, keyData)
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

def storeLinks(linkList, itemInstance, chunkSize, keyData):
    if len(linkList) > 0:
        key = EncryptionKey.getOrCreate(chunkSize=chunkSize, keydata=keyData)
        key.save()
        downloadFileGroup = DownloadFileGroup(itemInstance=itemInstance, key=key)
        downloadFileGroup.save()
        for link in linkList:
            df = DownloadFile(downloadFileGroup=downloadFileGroup,
                              downloadLink=link)
            df.save()


if __name__ == '__main__':
    main()
