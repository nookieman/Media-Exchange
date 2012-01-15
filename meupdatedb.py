#!/usr/bin/env python

import argparse
import os
import re
import sys
from ConfigParser import SafeConfigParser

from mediaExchange.movies.models import Movie, MovieSource, Language
from mediaExchange.series.models import Serie, Season, SerieSource

def addMovies(directory):
    #TODO check if still working with named groups
#    inforegex = re.compile('^(?P<title>.*?)(?:\s+-\s+(?P<subtitle>.*?))?(?:\s+\((?P<year>\d{4})\))?(?:\s+\[(?P<source>[a-zA-Z0-9!"$%&/()=\\\\?_-]*)\])?$')
    inforegex = re.compile('^(.*?)(?:\s+-\s+(.*?))?(?:\s+\((\d{4})\))?(?:\s+\[([a-zA-Z0-9!"$%&/()=\\\\?_-]*)\])?$')
    if os.path.isdir(directory):
        for mdir in os.listdir(directory):
            dirname = os.path.basename(mdir)
            mpath = directory + '/' + dirname
            match = inforegex.match(dirname)
            if match:
                (mname, msubname, myear, msource) = inforegex.match(dirname).groups()
                mmtime = int(os.stat(mpath).st_mtime)
                if msource:
                    # if the source of the movie does not exist create it
                    src = MovieSource.objects.filter(name=msource)
                    if src:
                        msource = src[0]
                    else:
                        msource = MovieSource(name=msource)
                        msource.save()
                rm = Movie.objects.filter(name=mname, subname=msubname, year=myear)
                if rm:
                    rm = rm[0]
                    if rm.mtime < mmtime:
                        rm.path = mpath
                        rm.mtime = mmtime
                        rm.size = getDirSize(mpath)
                        rm.save()
                else:
                    msize = getDirSize(mpath)
                    print (mname, msubname, myear, msource, msize)
                    m = Movie(name=mname, subname=msubname, path=mpath, year=myear, source=msource, mtime=mmtime, size=msize, present=True)
                    m.save()
            else:
                print "WARNING: invalid movie directory format '%s'" % dirname
    else:
        print 'ERROR: no such directory "%s"' % (directory)

def addSeries(directory):
    serieregex = re.compile('^(?P<title>.*?)$')
    seasonregex = re.compile('^s(?:eason)?\s*0*(\d+)(?:\s+-\s+(?P<subtitle>.*?))?(?:\s+\((?P<year>\d{4})\))?(?:\s+\[(?P<source>[a-zA-Z0-9!"$%&/()=\\\\?_-]*)\])?(?:\s+\|(?P<language>.*)\|)?$', re.I)
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
                            (seasonNumber, ssubname, syear, ssource, slanguage) = match.groups()
                            seasonPath = directory + '/' + serieDirName + '/' + seasonDirName
                            try:
                                serie = Serie.objects.get(name=serieName)
                            except Serie.DoesNotExist, e:
                                serie = Serie(name=serieName)
                                serie.save()
                            smtime = int(os.stat(seasonPath).st_mtime)
                            if ssource:
                                # if the source of the Series does not exist create it
                                try:
                                    ssource = SerieSource.objects.get(name=ssource)
                                except SerieSource.DoesNotExist, e:
                                    ssource = SerieSource(name=ssource)
                                    ssource.save()
                            if slanguage:
                                # if the language of the Series does not exist create it
                                try:
                                    slanguage = Language.objects.get(name=ssource)
                                except Language.DoesNotExist, e:
                                    slanguage = Language(name=ssource)
                                    slanguage.save()
                            directoryListing = ""
                            dirlist = os.listdir(seasonPath)
                            dirlist.sort()
                            for d in dirlist:
                                directoryListing += "%s\n" % d
                            directoryListing = directoryListing[:-1]
                            try:
                                season = Season.objects.get(serie=serie, number=seasonNumber, subname=ssubname, year=syear, language=slanguage, source=ssource)
                                if season.mtime < smtime:
                                    season.path = seasonPath
                                    season.mtime = smtime
                                    season.size = getDirSize(seasonPath)
                                    season.save()
                            except Season.DoesNotExist, e:
                                ssize = getDirSize(seasonPath)
                                print (serieName, seasonNumber, ssubname, syear, ssource, ssize)
                                season = Season(serie=serie, number=seasonNumber, subname=ssubname, path=seasonPath, year=syear, source=ssource, language=slanguage, mtime=smtime, size=ssize, directoryListing=directoryListing, present=True)
                                season.save()
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
