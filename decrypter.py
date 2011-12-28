#!/usr/bin/python

import sys, os, math
from Crypto.Cipher import Blowfish

ENCRYPTION_KEY = 'thisistheencryptionkey1234567890!"$%&/()=?+*#,.-;:_>.<'
ENCRYPTION_CHUNK_SIZE = 100000000

def joinFiles(files):
    print 'joinFiles(', files, ')'
    dfh = os.tmpfile()
    for file in files:
        filesize = os.stat(file).st_size
        print file, 'has size:', filesize
        sfh = open(file)
        for i in range(int(math.ceil(float(filesize)/float(ENCRYPTION_CHUNK_SIZE)))):
            dfh.write(sfh.read(ENCRYPTION_CHUNK_SIZE))
        sfh.close()
    return dfh

def decryptFile(fileHandle, outfile):
    print 'decryptFile(', fileHandle, outfile,')'
    blowfish = Blowfish.new(key=ENCRYPTION_KEY)
    dfh = open(outfile, 'wb')
    sfsize = fileHandle.tell()
    print "filesize is", sfsize
    fileHandle.seek(0)
    parts = int(math.ceil(float(sfsize)/float(ENCRYPTION_CHUNK_SIZE)))
    for i in range(parts):
        print "decrypt no", i
        dfh.write(blowfish.decrypt(fileHandle.read(ENCRYPTION_CHUNK_SIZE)))
    dfh.close()
    fileHandle.close()

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        files = sys.argv[1:-1]
        if len(files)>1:
            tfh = joinFiles(files)
        else:
            tfh = open(files[0])
            tfh.seek(0, os.SEEK_END)
        decryptFile(tfh, sys.argv[-1])
        print 'done.'
    else:
        print 'usage: %s <enc-file> [<enc-file> ...] <out-file>' % (sys.argv[0])

