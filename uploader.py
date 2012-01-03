#!/usr/bin/env python

import argparse
import atexit
import hashlib
import math
import os
import sys
import tarfile
import tempfile

from Crypto.Cipher import Blowfish

from medaemon import renice, cleanup
from MultiUpload import MultiUpload

def readKeyfile(keyfile):
    fh = open(keyfile)
    chunksize = int(fh.readline())
    key = fh.read()
    fh.close()
    return chunksize, key

def tarFiles(files):
    print "tarFiles", (files,)
    fh = tempfile.NamedTemporaryFile(suffix=".tar", delete=False)
    print fh.tell()
    for file in files:
        tar = tarfile.open(mode="w", fileobj=fh.file)
        tar.add(file)
    tar.close()
    fh.close()
    return fh.name

def createHash(files):
    hashString = ";".join(files)
    return hashlib.sha1(hashString).hexdigest()

def encryptFile(file, outfilename, chunksize, key):
    print "encryptFile", (file, outfilename, chunksize, "...")
    tmpDir = tempfile.mkdtemp()
    tmpfilePath = "%s/%s.tar" % (tmpDir, outfilename)
    blowfish = Blowfish.new(key)
    destfh = open(tmpfilePath, 'wb')
    sourcefh = open(file, 'rb')
    sourceSize = os.stat(file).st_size
    parts = int(math.ceil(float(sourceSize)/float(chunksize)))
    for i in range(parts):
        destfh.write(blowfish.encrypt(sourcefh.read(chunksize)))
        percent = int((i+1)/float(parts)*100.0)
        print percent, "%"
    destfh.close()
    sourcefh.close()
    return tmpfilePath

def splitFile(file, maxSize):
    print "splitFile", (file, maxSize)
    result = [file]
    fileSize = os.stat(file).st_size
    if fileSize > maxSize:
        result = []
        parts = int(math.ceil(float(fileSize) / float(maxSize)))
        sfh = open(file, 'rb')
        for part in range(parts):
            tmpfile = "%s.%3d" % (file, part)
            print 'packing part', part, 'filename:', tmpfile
            dfh = open(tmpfile, 'wb')
            for i in range(1000):
                dfh.write(sfh.read(int(math.ceil(float(maxSize)/float(1000)))))
                percent = int((part+1)*(float(i+1)/1000.0)/parts*100)
                print percent, "%"
            dfh.close()
            result.append(tmpfile)
    return result

def uploadFiles(files):
    print 'uploadFiles', (files,)
    links = []
    mu = MultiUpload()
    for file in files:
        links.append(mu.uploadData(file))
    return links

if __name__=="__main__":
    parser = argparse.ArgumentParser("Upload a file for usage in a Media Exchange instance. The output folder will afterwards contain two files. links.txt: the list of download links seperated by linebreaks. keyfile.txt: the keyfile needed to decrypt the files.")
    parser.add_argument('-c', '--chunk-size', dest="chunksize", type=int, default=10000000, help="define the encryption chunk size (default: 10000000)")
    parser.add_argument('-k', '--keyfile', dest="keyfile", help="keyfile to use for encryption")
    parser.add_argument('-n', '--nice', dest="nice", default=15, help="set the nice level (default: 15)")
    parser.add_argument('-r', '--random-key', dest="keysize", type=int, default=0, help="create a new random key of a defined size")
    parser.add_argument('inputfiles', metavar="INPUT-FILE", nargs="+", help="the files and/or folders to be uploaded")
    parser.add_argument('outputfolder', metavar="OUTPUT-FOLDER", help="resulting key and download urls will be placed in this folder")
    args = parser.parse_args()

    if args.keyfile:
        chunksize, key = readKeyfile(args.keyfile)
    elif args.keysize and args.chunksize:
        print "ERROR: sorry currently not implemented"
        sys.exit(-1)
    renice(args.nice)

#    atexit.register()

    tarFile = tarFiles(args.inputfiles)
    hashname = createHash(args.inputfiles)
    encryptedFile = encryptFile(tarFile, hashname, chunksize, key)
    cleanup(tarFile)
    splittedFiles = splitFile(encryptedFile, MultiUpload.MAX_FILESIZE)
    cleanup(encryptedFile)
    links = uploadFiles(files=splittedFiles)
    print links
    cleanup(splittedFiles)
    if not os.path.exists(args.outputfolder):
        os.mkdir(args.outputfolder)
    keyfile = open("%s/keyfile.txt" % args.outputfolder, 'w')
    keyfile.write("%s\n%s" % (chunksize, key))
    keyfile.close()
    linksfile = open("%s/links.txt" % args.outputfolder, 'w')
    linksfile.write("\n".join(links))
    linksfile.close()
