#!/usr/bin/python

import filecmp

from decrypter import joinFiles, decryptFile, ENCRYPTION_KEY, ENCRYPTION_CHUNK_SIZE
from medaemon import tarDownload, splitFile, encryptDownload, cleanup, MAX_FILE_SIZE

infile = '/tmp/enctest'
outfile = '/tmp/enctest-result'

print "Creating input file."
fh = open(infile, 'wb')
for i in range(1000000):
    fh.write(str(i)[-1]*2000)

print "Taring input file."
tarfile = tarDownload(infile)
print "Encrypting tar file."
encfile = encryptDownload(tarfile)
print "Splitting encrypted file."
encfiles = splitFile(encfile)
print "Joining encrypted parts."
tfh = joinFiles(encfiles)
print "Decrypting whole encrypted file."
decryptFile(tfh, outfile)


print "Checking for differences:"
if filecmp.cmp(tarfile, outfile):
    print "SUCCESS"
else:
    print "FAILED"

#print "Cleaning up files."
#filelist = [tarfile, encfile] + encfiles
#cleanup(filelist)
