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
import urllib2
import argparse
import os
import sys, codecs, locale
import ConfigParser
import re
import time
from xml.dom.minidom import parseString


def urlRetry(url):
    failCount = 0
    success = False
    data = {}
    while failCount < 5 and success is False:
        try:
            data = urllib2.urlopen(url).read()
        except IOError:
            failCount = failCount + 1
            print "tvrage error, retrying in 1 second"
            time.sleep(1)
        else:
            success = True

    if success is False:
        raise Exception('Too many failures - I give up!')
    
    return data


def descape (html):
    return html.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', '\'')


def getShowId (title):
    searchstring = title.replace('.','+').replace(' ','+')
    cachedir = '/tmp/.tvshowidcache/'
    cachefile = cachedir + searchstring
    
    ensureDir(cachedir)
    if not(os.path.isfile(cachefile)):
        data = urlRetry('http://services.tvrage.com/myfeeds/search.php?key=sCG8WH681LBuwaqyNNlf&show=' + searchstring)
        file = open(cachefile,"w")
        file.write(data)
        file.close()
        
    data = open(cachefile).read()
    dom = parseString(data)
    return int(dom.getElementsByTagName('showid')[0].toxml().replace('<showid>','').replace('</showid>',''))

def clearCache():
    cachedir = '/tmp/.tvcache/'
    if os.path.exists(cachedir):
        nukeDir(cachedir)

def nukeDir(directory):
    if directory[-1] == os.sep: directory = directory[:-1]
    files=os.listdir(directory)
    for f in files:
        if f=='.' or f=='..': continue
        path = directory + os.sep + f
        if os.path.isdir(path):
            nukeDir(directory)
        else:
            os.unlink(path)
    os.rmdir(directory)

def ensureDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def exerciseTag(formatStyle, tag, showid, seasonnum, episode):
    realTag = re.compile(tag, re.IGNORECASE).findall(formatStyle)
        
    if len(realTag) < 1:
        return formatStyle

    realTag = realTag[0]
    if len(realTag) > 1 and realTag[1] == '.':
        formatStyle = formatStyle.replace(realTag, getData(showid, seasonnum, episode, realTag.replace('%', '').replace('.', '')).replace(' ', '.'))
    else:
        formatStyle = formatStyle.replace(realTag, getData(showid, seasonnum, episode, realTag.replace('%', '')))

    return descape(exerciseTag(formatStyle, tag, showid, seasonnum, episode))


def buildFileName(showid, seasonnum, episodes):
    episode = episodes[0]
    episodeOut = ""
    for ep in episodes:
        episodeOut += str(ep).zfill(2)

    config = ConfigParser.RawConfigParser()
    config.read(['/etc/kirk.conf', '/usr/local/etc/kirk.conf', os.path.expanduser('~/.kirkrc')])
        
    formatStyle = config.get('output', 'format')
    
    formatStyle = exerciseTag(formatStyle, '%name%',         showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%title%',        showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%season%',       showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%epnum%',        showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%prodnum%',      showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%airdate%',      showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%link%',         showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%rating%',       showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%screencap%',    showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%totalseasons%', showid, seasonnum, episode)
    
    formatStyle = exerciseTag(formatStyle, '%\.name\.%',         showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.title\.%',        showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.season\.%',       showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.epnum\.%',        showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.prodnum\.%',      showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.airdate\.%',      showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.link\.%',         showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.rating\.%',       showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.screencap\.%',    showid, seasonnum, episode)
    formatStyle = exerciseTag(formatStyle, '%\.totalseasons\.%', showid, seasonnum, episode)
    
    realTag = re.compile('%.*episode.*%', re.IGNORECASE).findall(formatStyle)
    if len(realTag) > 0:
        formatStyle = formatStyle.replace(realTag[0], episodeOut)

    return formatStyle

def csv(value):
    return map(int, value.split(","))


def getName(showTitle, showid, seasonNum, episodeNums):
    if showid == None:
        showid = getShowId(showTitle)
    else:
        showid = showid[0]

    return buildFileName(showid, seasonNum, episodeNums)


def getXML(xml, field):
    item = xml.toxml().replace('<' + field.lower() + '>','').replace('</' + field.lower() + '>','').replace('<' + field.lower() + '/>','')
    if field.lower() == field:
        return item.lower()
    elif field.upper() == field:
        return item.upper()
    else:
        return item


def getData(showid, seasonNum, episodeNum, field):
    output = ""

    if field.lower() == "episode":
        if field.lower() == field:
                field = "seasonnum"
        elif field.upper() == field:
                field = "SEASONNUM"
        else:
                field = "Seasonnum"

    cachedir = '/tmp/.tvcache/'
    ensureDir(cachedir)
    cachefile = (cachedir + `showid`).encode('ascii')
    if not(os.path.isfile(cachefile)):
        data = urlRetry('http://services.tvrage.com/myfeeds/episode_list.php?key=sCG8WH681LBuwaqyNNlf&sid=' + `showid`)
        file = open(cachefile,"w")
        file.write(data)
        file.close()

    data = open(cachefile).read()
    dom = parseString(data)

    if field.lower() == "name" or field.lower() == "totalseasons":
        elements = dom.getElementsByTagName(field.lower())
        if len(elements) > 0:
            return getXML(elements[0], field)
        
    if field.lower() == "season":
        return str(seasonNum).zfill(2)

    seasonxml = parseString(dom.getElementsByTagName('Season')[seasonNum-1].toxml())
    elements = seasonxml.getElementsByTagName(field.lower())


    if len(elements) >= int(episodeNum):
        output = getXML(elements[int(episodeNum)-1], field)

    return output

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    cachedir = '/tmp/.tvcache/'
    
    parser = argparse.ArgumentParser(description='Get nicely formatted filename.')
    parser.add_argument('showtitle', metavar='ShowTitle', type=str, nargs=1, help="Show Title")
    parser.add_argument('seasonnum', metavar='Season', type=int, nargs=1, help='Season Number')
    parser.add_argument('episodenums', metavar='Episode(s)', type=csv, nargs=1, help='Episode Number(s)')
    parser.add_argument('--showid', metavar='ShowID', dest='showid', type=int, nargs=1, help='The TVRage Show ID Number')
    parser.add_argument('--clear-cache', dest='clearcache', action='store_const', const="true", default="false", help="clear the cache")
        
    args = parser.parse_args()

    
    if args.clearcache == "true":
        clearCache()
        return 0

    print getName(args.showtitle[0], args.showid, args.seasonnum[0], args.episodenums[0]),

    return 0

if __name__ == "__main__":
    main()
