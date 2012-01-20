#!/usr/bin/env python

import argparse
import os
import re
import sys
from ConfigParser import SafeConfigParser

from mediaExchange.movies.models import Movie, Source, Language, ItemInstance
from mediaExchange.series.models import Serie, Season

def addMovies(directory):
    #TODO check if still working with named groups
#    inforegex = re.compile('^(?P<title>.*?)(?:\s+-\s+(?P<subtitle>.*?))?(?:\s+\((?P<year>\d{4})\))?(?:\s+\[(?P<source>[a-zA-Z0-9!"$%&/()=\\\\?_-]*)\])?$')
    inforegex = re.compile('^(?P<name>.*?)(?:\s+-\s+(?P<subname>.*?))?(?:\s+\((?P<year>\d{4})\))?(?:\s+\[(?P<source>[a-zA-Z0-9!"$%&/()=\\\\?_-]*)\])?$')
    if os.path.isdir(directory):
        for mdir in os.listdir(directory):
            dirname = os.path.basename(mdir)
            mpath = directory + '/' + dirname
            match = inforegex.match(dirname)
            if match:
                movieDict = inforegex.match(dirname).groupdict()
                mmtime = int(os.stat(mpath).st_mtime)
                msource = Source.getOrCreate(movieDict.get('source', None))
                movie = Movie.getOrCreate(name=movieDict['name'],
                                          subname=movieDict.get('subname', None),
                                          year=movieDict.get('year', None))
                try:
                    itemInstance = ItemInstance.objects.get(path=mpath)
                    if itemInstance.mtime < mmtime:
                        itemInstance.path = mpath
                        itemInstance.mtime = mmtime
                        itemInstance.size = getDirSize(mpath)
                        itemInstance.save()
                except ItemInstance.DoesNotExist:
                    msize = getDirSize(mpath)
                    print movieDict
                    itemInstance = ItemInstance(item=movie,
                              path=mpath,
                              source=msource,
                              mtime=mmtime,
                              size=msize,
                              present=True)
                    itemInstance.save()
            else:
                print "WARNING: invalid movie directory format '%s'" % dirname
    else:
        print 'ERROR: no such directory "%s"' % (directory)

def addSeries(directory):
    serieregex = re.compile('^(?P<title>.*?)$')
    seasonregex = re.compile('^s(?:eason)?\s*0*(?P<number>\d+)(?:\s+-\s+(?P<subtitle>.*?))?(?:\s+\((?P<year>\d{4})\))?(?:\s+\[(?P<source>[a-zA-Z0-9!"$%&/()=\\\\?_-]*)\])?(?:\s+\|(?P<language>.*)\|)?$', re.I)
    if os.path.isdir(directory):
        for serieDir in os.listdir(directory):
            seriePath = directory + '/' + serieDir
            if os.path.isdir(seriePath):
                serieDirName = os.path.basename(serieDir)
                serieName = serieregex.match(serieDirName).group(1)
                for seasonDir in os.listdir(seriePath):
                    if os.path.isdir(seriePath + '/' + seasonDir):
                        seasonDirName = os.path.basename(seasonDir)
                        match = seasonregex.match(seasonDirName)
                        if match:
                            seasonDict = match.groupdict()
                            seasonNumber = seasonDict['number']
                            ssubname = seasonDict.get('subtitle', None)
                            syear = seasonDict.get('year', None)
                            seasonPath = directory + '/' + serieDirName + '/' + seasonDirName
                            serie = Serie.getOrCreate(name=serieName)
                            smtime = int(os.stat(seasonPath).st_mtime)
                            ssource = Source.getOrCreate(name=seasonDict.get('source', None))
                            slanguage = Language.getOrCreate(name=seasonDict.get('language', None))
                            directoryListing = ""
                            dirlist = os.listdir(seasonPath)
                            dirlist.sort()
                            for d in dirlist:
                                directoryListing += "%s\n" % d
                            directoryListing = directoryListing[:-1]
                            season = Season.getOrCreate(serie=serie,
                                                        number=seasonNumber,
                                                        subname=ssubname,
                                                        year=syear)
                            try:
                                itemInstance = ItemInstance.objects.get(path=seasonPath)
                                if itemInstance.mtime < smtime:
                                    itemInstance.path = seasonPath
                                    itemInstance.mtime = smtime
                                    itemInstance.size = getDirSize(seasonPath)
                                    itemInstance.save()
                            except ItemInstance.DoesNotExist:
                                ssize = getDirSize(seasonPath)
                                print (serieName, seasonNumber, ssubname, syear, ssource, ssize)
                                itemInstance = ItemInstance(item=season,
                                                            path=seasonPath,
                                                            source=ssource,
                                                            language=slanguage,
                                                            mtime=smtime,
                                                            size=ssize,
#                                                            directoryListing=directoryListing,
                                                            present=True)
                                itemInstance.save()
                        else:
                            print "WARNING: invalid season directory format '%s'" % seasonDirName
                    else:
                        print "WARNING: season directory contains invalid file '%s'" % seasonDir
            else:
                print 'WARNING: invalid file in series directory "%s"' % serieDir
    else:
        print 'ERROR: no such directory "%s"' % (directory)

def calcDirSize(arg, dir, files):
    for file in files:
        stats = os.stat(os.path.join(dir, file))
        size = stats[6]
        arg.append(size)

def getDirSize(dir):
    sizes = []
    os.path.walk(dir, calcDirSize, sizes)
    total = 0
    for size in sizes:
        total = total + size
#    if total > 1073741824:
#        return (round(total/1073741824.0, 2), 'GB')
#    if total > 1048576:
#        return (round(total/1048576.0, 2), 'MB')
#    if total > 1024:
#        return (round(total/1024.0, 2), 'KB')
    return total

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Update the Media Exchange Database based on a config file.')
    parser.add_argument('config', metavar="config", type=str, help="config file to use")
    args = parser.parse_args()

    cp = SafeConfigParser()
    cp.read(args.config)
    defaults = cp.defaults()
    if 'movies' in defaults:
        for movieDir in [m.strip() for m in defaults['movies'].split(',')]:
            addMovies(movieDir)

    if 'series' in defaults:
        for serieDir in [m.strip() for m in defaults['series'].split(',')]:
            addSeries(serieDir)
