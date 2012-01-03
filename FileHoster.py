import time

class FileHoster(object):

    STATE_QUEUED = 0
    STATE_TARING = 1
    STATE_ENCRYPTING = 2
    STATE_SPLITTING = 3
    STATE_UPLOADING = 4


    MAX_FILESIZE = 1000000 # in bytes

    def uploadData(self, fh):
        raise Exception("Not Implemented!")

    def updateUploadState(self, uploadRequest, filehandle, totalsize):
        print 'updateUploadState(', uploadRequest, ',', filehandle, ',', totalsize, ')'
        done = False
        uploadRequest.state = self.STATE_UPLOADING
        while not done:
            time.sleep(10)
            cur = filehandle.tell()
            percent = int((cur+1)/float(totalsize)*100)
#        print percent
            uploadRequest.uploaded = percent
            uploadRequest.save()
            if totalsize == cur:
                filehandle.close()
                done = True

