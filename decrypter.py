#!/usr/bin/python

import argparse
import math
import os
import sys
from Crypto.Cipher import Blowfish

def joinFiles(files, chunkSize):
    print 'joinFiles(', files, chunkSize, ')'
    dfh = os.tmpfile()
    for file in files:
        filesize = os.stat(file).st_size
        print file, 'has size:', filesize
        sfh = open(file)
        for i in range(int(math.ceil(float(filesize)/float(chunkSize)))):
            dfh.write(sfh.read(chunkSize))
        sfh.close()
    return dfh

def decryptFile(fileHandle, outfile, key, encryptionChunkSize):
    print 'decryptFile(', fileHandle, outfile, key, encryptionChunkSize, ')'
    blowfish = Blowfish.new(key=key)
    dfh = open(outfile, 'wb')
    sfsize = fileHandle.tell()
    print "filesize is", sfsize
    fileHandle.seek(0)
    parts = int(math.ceil(float(sfsize)/float(encryptionChunkSize)))
    for i in range(parts):
        print "decrypt no", i
        dfh.write(blowfish.decrypt(fileHandle.read(encryptionChunkSize)))
    dfh.close()
    fileHandle.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Decrypt a file downloaded from MediaExchange.')
    parser.add_argument('-k', '--keyfile', type=str, dest="keyfile", required=True, help="file containing the key to decrypt the file")
    parser.add_argument('encfiles', metavar="enc-file", type=str, nargs="+", help="encrypted input files")
    parser.add_argument('outfile', metavar="out-file", type=str, help="output file")
    args = parser.parse_args()

    keyfilehandle = open(args.keyfile)
    encryptionChunkSize = int(keyfilehandle.readline())
    key = keyfilehandle.read()

    if len(args.encfiles)>1:
        tfh = joinFiles(files)
    else:
        tfh = open(args.encfiles[0])
        tfh.seek(0, os.SEEK_END)
    decryptFile(tfh, args.outfile, key, encryptionChunkSize)
    print 'done.'
