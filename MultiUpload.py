import os
import re
import threading
import urllib2

from FileHoster import FileHoster

from mediaExchange.movies.models import DownloadFile
from mediaExchange.poster.encode import multipart_encode
from mediaExchange.poster.streaminghttp import register_openers

class MultiUpload(FileHoster):
        
    MAX_FILESIZE = 500000000 # in bytes

    PREURL = "http://multiupload.com/"

    DOWNLOADLINK_REGEX = re.compile("\"downloadid\":\"([^\"]+)\"", re.I | re.S | re.M)
    UPLOADIDENTIFIER_REGEX = re.compile("multiupload\.com\/upload\/\?UPLOAD\_IDENTIFIER\=([^\"]+)\"", re.I | re.S | re.M)
    USERCOOKIE_REGEX = re.compile("name\=\"u\" value\=\"([^\"]+)\"", re.I | re.S | re.M)
    UPLOADURL_REGEX = re.compile("enctype=\"multipart\/form-data\" action=\"([^\"]+)\" method=\"POST\"", re.I | re.S | re.M)
    
    def getNeededValues(self):
        uploadURL = None
        uploadIdentifier = None
        usercookie = None
        source = urllib2.urlopen(self.PREURL).read()
        match = self.UPLOADURL_REGEX.search(source)
        if match:
            uploadURL = match.group(1)
        else:
            print source
            print "ERROR: unable to find uploadURL"
        match = self.UPLOADIDENTIFIER_REGEX.search(source)
        if match:
            uploadIdentifier = match.group(1)
        else:
            print source
            print "ERROR: unable to find uploadIdentifier"
        match = self.USERCOOKIE_REGEX.search(source)
        if match:
            usercookie = match.group(1)
        else:
            print source
            print "ERROR: unable to find usercookie"
        return uploadURL, uploadIdentifier, usercookie


    def uploadData(self, filename, uploadRequest):
        uploadURL, uploadIdentifier, usercookie = self.getNeededValues()
        register_openers()
        fh = open(filename)
        datagen, headers = multipart_encode(
            {
                "UPLOAD_IDENTIFIER" : uploadIdentifier,
                "u" : usercookie,
                "remember_18" : 1,
                "password_18" : "",
                "username_18" : "",
                "remember_14" : 1,
                "password_14" : "",
                "username_14" : "",
                "remember_15" : 1,
                "password_15" : "",
                "username_15" : "",
                "remember_6" : 1,
                "password_6" : "",
                "username_6" : "",
                "remember_17" : 1,
                "password_17" : "",
                "username_17" : "",
                "remember_9" : 1,
                "password_9" : "",
                "username_9" : "",
                "remember_7" : 1,
                "password_7" : "",
                "username_7" : "",
                "remember_16" : 1,
                "password_16" : "",
                "username_16" : "",
                "remember_1" : 1,
                "password_1" : "",
                "username_1" : "",
                "toemail" : "",
                "fromemail" : "",
                "service_18" : 1,
                "service_14" : 1,
                "service_15" : 1,
                "service_6" : 1,
                "service_17" : 1,
                "service_9" : 1,
                "service_7" : 1,
                "service_16" : 1,
                "service_1" : 1,
                "fetchdesc9" : "",
                "fetchfield9" : "http://",
                "fetchdesc8" : "",
                "fetchfield8" : "http://",
                "fetchdesc7" : "",
                "fetchfield7" : "http://",
                "fetchdesc6" : "",
                "fetchfield6" : "http://",
                "fetchdesc5" : "",
                "fetchfield5" : "http://",
                "fetchdesc4" : "",
                "fetchfield4" : "http://",
                "fetchdesc3" : "",
                "fetchfield3" : "http://",
                "fetchdesc2" : "",
                "fetchfield2" : "http://",
                "fetchdesc1" : "",
                "fetchfield1" : "http://",
                "description_9" : "",
                "description_8" : "",
                "description_7" : "",
                "description_6" : "",
                "description_5" : "",
                "description_4" : "",
                "description_3" : "",
                "description_2" : "",
                "description_1" : "",
                "file_0" : fh,
                "fetchdesc0" : "",
                "fetchfield0" : "",
                "description_0" : "",
            })
        headers.update({'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.10) Gecko/2009042523 Ubuntu/9.04 (jaunty) Firefox/3.0.10'})
        t = threading.Thread(target=self.updateUploadState, args=(uploadRequest, fh, os.stat(filename).st_size))
        t.start()
        request = urllib2.Request(uploadURL, datagen, headers)
        source = urllib2.urlopen(request).read()
        match = self.DOWNLOADLINK_REGEX.search(source)
        df = None
        if match:
            dlLink = "http://multiupload.com/%s" % match.group(1)
            df = DownloadFile(item=uploadRequest.item, downloadLink=dlLink)
            df.save()
            print "download:", df
        else:
            print source
            print "ERROR: cannot fetch download link for MultiUpload"
        return df
