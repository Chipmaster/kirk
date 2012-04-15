#!/usr/bin/env python
#
#    Copyright (C) <year>  <name of author>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, os, re
import argparse
import subprocess
import ConfigParser

import tvrage

def traverseDirectory(target, showid, dryrun):
    dirList = os.listdir(target)
    for d in dirList:
        if os.path.isdir(target + "/" + d):
            traverseDirectory(target + "/" + d, showid, dryrun)
        else:
            fixFile(d, target, showid, dryrun)

def fixFile(target, directory, showid, dryrun):
    extension = os.path.splitext(target)[1][1:]

    config = ConfigParser.RawConfigParser()
    config.read(['/etc/kirk.conf', '/usr/local/etc/kirk.conf', os.path.expanduser('~/.kirkrc')])

    seriesParse  = tuple([ item[1] for item in config.items('input') if item[0].startswith("series")])
    seasonParse  = tuple([ item[1] for item in config.items('input') if item[0].startswith("season")])
    episodeParse = tuple([ item[1] for item in config.items('input') if item[0].startswith("episode")])

    i = 0
    while i < len(seriesParse) and re.compile(seriesParse[i]).match(target) == None:
        i += 1

    if i == len(seriesParse):
        print "Could not parse: " + target
        return

    title = re.compile(seriesParse[i]).match(target).group(1)
    season = re.compile(seasonParse[i]).match(target).group(1)
    episodes = re.compile(episodeParse[i]).match(target).groups()

    newfile = ""
    if showid != None:
        if dryrun == 'true':
            print "call to tvrage.py = tvrage.py " + title + " " + season + \
                  " " + str(episodes) + " --showid " + `showid`
        showid = [showid]
        newfile = tvrage.getName(title, showid, int(season), episodes)


    else:
        if dryrun == 'true':
            print "call to tvrage.py = tvrage.py " + title + " " + season + \
                  " " + str(episodes)
        newfile = tvrage.getName(title, None, int(season), episodes)

    source = os.path.normpath(directory + "/" + target)
    if newfile[len(newfile) - 1] != '.':
        print "Renaming: " + target + "  to:  " + newfile + "." + extension
        dest = os.path.normpath(directory + "/" + newfile + "." + extension)
    else:
        print "Renaming: " + target + "  to:  " + newfile + extension
        dest = os.path.normpath(directory + "/" + newfile + extension)

    if dryrun != 'true':
        if target != (newfile + extension):
            os.rename(source, dest)

 

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    parser = argparse.ArgumentParser(description='Rename TV Files')
    parser.add_argument('target', metavar='Target', type=str, nargs=1, 
                        help='Target Directory or File')
    parser.add_argument('-s', '--showid', metavar='ShowID', dest='showid', 
                        type=int, nargs=1, help='The TVRage Show ID Number')
    parser.add_argument('-d', '--dry-run', dest='dryrun', action='store_const', 
                        const="true", default="false", help="Perform a dry run "
                        "showing what will happen")
    
    args = parser.parse_args()
    
    target = args.target[0]
    if args.showid != None:
        showid = args.showid[0]
    else:
        showid = None
    dryrun = args.dryrun

    if not os.path.exists(target):
        print "Target does not exist"
        return 1

    #clear tv show cache
    tvrage.clearCache()
    
    if os.path.isdir(target):
        traverseDirectory(target, showid, dryrun)
    else:
        directory = os.path.dirname(target)
        if directory == "":
            directory = "."
        f = os.path.basename(target)
        fixFile(f, directory, showid, dryrun)
        
    return 0

if __name__ == "__main__":
    main()
