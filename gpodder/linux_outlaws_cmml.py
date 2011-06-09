#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Hooks script for gPodder to create a CMML file
# containing chapters for Linux Outlaws.
#
# Version 1.0 - Copyright (C) 2011 Eric Le Lay <neric27@wanadoo.fr>
# 
# To use, copy it as a Python script into ~/.config/gpodder/hooks/linux_outlaws_cmml.py
#
# Dependencies:
# * This script needs the BeautifulSoup
#    http://www.crummy.com/software/BeautifulSoup/documentation.html
#   In gentoo, it's included in the beautifulsoup package.
# * It also uses xml.etree, which comes with recent
#    python versions (tested with python 2.7)
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# gPodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gpodder
from gpodder.liblogger import log,enable_verbose

import urllib2
import BeautifulSoup
from BeautifulSoup import BeautifulSoup


import re
import sys
from xml.etree import ElementTree as ET

def create_cmml(html, ogg_file):
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    time_re  = text=re.compile("\\d{1,2}(:\\d{2}){2}")
    times = soup.findAll(text=time_re)
    if len(times) > 0:
        m = re.match('(.*)\\.[^\\.]+$',ogg_file)
        if m is not None:
            to_file = m.group(1) + ".cmml"
            cmml = ET.Element('cmml',attrib={'lang':'en'})
            remove_ws = re.compile('\s+')
            for t in times:
                txt = ''
                for c in t.parent.findAll(text=True):
                    if c is not t: txt += c
                txt = remove_ws.sub(' ', txt)
                txt = txt.strip()
                log("found chapter %s at %s"%(txt,t))
                # totem want's escaped html in the title attribute (not &amp; but &amp;amp;)
                txt = txt.replace('&','&amp;')
                clip = ET.Element('clip')
                clip.set('id',t)
                clip.set( 'start', ('npt:'+t))
                clip.set('title',txt)
                cmml.append(clip)
            ET.ElementTree(cmml).write(to_file,encoding='utf-8')

def create_cmml_from_file(ogg_file):
    m = re.match('(.*linuxoutlaws)([0-9]+)\\.(ogg|mp3)',ogg_file)
    if m is not None:
    	episode_num = m.group(2)
    	url = 'http://linuxoutlaws.com/podcast/ogg/' + episode_num
    	log("downloading show notes for episode %s" % episode_num)
    	page = urllib2.urlopen(url)
    	create_cmml(page,ogg_file)
    else:
    	print("not a Linux Outlaws file !")

class gPodderHooks(object):
    def __init__(self):
        log('linux_outlaws_cmml extension: Initializing.')

    def on_episode_downloaded(self, episode):
        log('linux_outlaws_cmml: on_episode_downloaded(%s, %s)' % (episode.title, episode.channel.url))
        # may have to change that if the feed is renamed...
        if episode.channel.title.startswith('Linux Outlaws'):
        	html = episode.description
        	ogg_file = episode.local_filename(False)
        	# if html notes don't work for you, use create_cmml_from_file
        	# instead of create_cmml
        	# create_cmml_from_file(ogg_file)
        	create_cmml(html,ogg_file)

if __name__ == '__main__':
    enable_verbose()
    if len(sys.argv) != 2:
        print("Usage: %s PATH_TO_LINUXOUTLAWSEPISODEXXX.ogg"%sys.argv[0])
    else:
        ogg_file = sys.argv[1]
        create_cmml_from_file(ogg_file)
