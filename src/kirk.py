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

def ensureDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def nukeDir(directory):
    if directory[-1] == os.sep: directory = directory[:-1]
    files = os.listdir(directory)
    for f in files:
        if f=='.' or f=='..': continue
        path = directory + os.sep + f
        if os.path.isdir(path):
            nukeDir(directory)
        else:
            os.unlink(path)
    os.rmdir(directory)

def traverseDirectory(target, showid, debug, backup):
    dirList = os.listdir(target)
    for d in dirList:
        if os.path.isdir(target + "/" + d):
            if d == ".kirk-backup":
               if backup:
                   nukeDir(target + "/" + d)
            else:
                traverseDirectory(target + "/" + d, showid, debug, backup)
        else:
            fixFile(d, target, showid, debug, backup)

def fixFile(target, directory, showid, debug, backup):
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

    if showid == None and title == "":
        print "Could not determine series for " + target
        return

    if debug and showid != None:
        print "Using showid: " + `showid[0]`
    elif debug:
        print "Determining showid from: " + title

    if debug:
        print "call to tvrage.py = tvrage.py " + title + " " + season + \
            " " + str(episodes) + " --showid " + `showid`
    newfile = tvrage.getName(title, showid, int(season), episodes)

    source = os.path.normpath(directory + "/" + target)
    if newfile[len(newfile) - 1] != '.':
        if debug:
            print "Renaming: " + target + "  to:  " + newfile + "." + extension
        dest = os.path.normpath(directory + "/" + newfile + "." + extension)
    else:
        if debug:
            print "Renaming: " + target + "  to:  " + newfile + extension
        dest = os.path.normpath(directory + "/" + newfile + extension)

    if target != (newfile + extension):
        if backup:
            backupDir = directory + "/.kirk-backup"
            ensureDir(backupDir)
            
            backupFile = backupDir + "/" + target
            if os.path.exists(backupFile):
                os.remove(backupFile)

            os.link(source, backupFile)
        
        os.rename(source, dest)

 

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    parser = argparse.ArgumentParser(description='Rename TV Files')
    parser.add_argument('target', metavar='Target', type=str, nargs=1, 
                        help='Target Directory or File')
    parser.add_argument('-s', '--showid', metavar='ShowID', dest='showid', 
                        type=int, nargs=1, help='The TVRage Show ID Number')
    parser.add_argument('-D', '--debug', dest='debug', action='store_true', 
                        default=False, help="Show debugging "
                        "information")
    parser.add_argument('-B', '--backup', dest='backup', action='store_true', 
                        default=False, help="Create a backup directory with "
                        "the old file names as hard links to the new files")

    args = parser.parse_args()
    
    target = args.target[0]
    showid = args.showid
    debug = args.debug
    backup = args.backup

    if not os.path.exists(target):
        print "Target does not exist"
        return 1

    #clear tv show cache
    tvrage.clearCache()
    
    if os.path.isdir(target):
        traverseDirectory(target, showid, debug, backup)
    else:
        directory = os.path.dirname(target)
        if directory == "":
            directory = "."
        f = os.path.basename(target)
        fixFile(f, directory, showid, debug, backup)
        
    return 0

if __name__ == "__main__":
    main()
