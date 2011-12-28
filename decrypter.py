#!/usr/bin/python

import argparse
import math
import os
import sys
from Crypto.Cipher import Blowfish

#import rsa
#from rsa.bigfile import decrypt_bigfile

ENCRYPTION_KEY = 'thisistheencryptionkey1234567890!"$%&/()=?+*#,.-;:_>.<'
ENCRYPTION_CHUNK_SIZE = 100000000
#PRIVATE_KEY = "/tmp/privKey.pem"

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

#def decryptFileRSA(fileHandle, outfile):
#    print "decryptFileRSA(", fileHandle, outfile,")"
#    privKey = rsa.PrivateKey.load_pkcs1(open(PRIVATE_KEY).read())
#    outfileHandle = open(outfile, 'w')
#    decrypt_bigfile(fileHandle, outfileHandle, privKey)
#    outfileHandle.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Decrypt a file downloaded from MediaExchange.')
    parser.add_argument('encfiles', metavar="enc-file", type=str, nargs="+", help="encrypted input files")
    parser.add_argument('outfile', metavar="out-file", type=str, help="output file")
    args = parser.parse_args()

#    if len(sys.argv) >= 3:
#        files = sys.argv[1:-1]
    if len(args.encfiles)>1:
        tfh = joinFiles(files)
    else:
        tfh = open(args.encfiles[0])
        tfh.seek(0, os.SEEK_END)
    decryptFile(tfh, args.outfile)
    print 'done.'
#    else:
#        print 'usage: %s <enc-file> [<enc-file> ...] <out-file>' % (sys.argv[0])

