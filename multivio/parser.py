#!/usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser
from xml.dom.minidom import parseString
import urllib2
import json
#import simplejson as json

# third party modules


# local modules
import cdm

class ParserSelector:
    def __init__(self):
        #self._mods = ModsParser()
        #self._marc = MarcParser()
        self._dc = DublinCoreParser()
    
    def parseFile(self, file_name):
        f = file(file_name)
        content = f.read()
        f.close()
        return self._parse(content)
    
    def parseUrl(self, query_url):
        #print query_url
        content = urllib2.urlopen(query_url).read()
        return self._parse(content)

    def _parse(self, content):
        self._dc = DublinCoreParser()
        doc = parseString(content)
        root = doc.documentElement
        #if root.namespaceURI == 'http://www.loc.gov/mods/v3':
        #    self._mods.parse(root)
        #    return self._mods
        #
        #if root.namespaceURI == 'http://www.loc.gov/MARC21/slim':
        #    self._marc.parse(root)
        #    return self._marc
    
        dc = root.getElementsByTagName('dc:dc')
        if len(dc) and dc[0].namespaceURI == 'http://purl.org/dc/elements/1.1/':
            self._dc.parse(doc)
            return self._dc
            
    
class Parser:
    def __init__(self):
        self._cdm = cdm.CoreDocumentModel()
    
    def json(self):
        return json.dumps(self._cdm)
        
    def display(self):
        print self.json()


class DublinCoreParser(Parser):
    def __init__(self):
        Parser.__init__(self)
    
    def parse(self, root):
        
        records = root.getElementsByTagName('collection')

        # get the id number of the first record
        if len(records) == 0:
                print "No mods"
        if len(records) > 1:
                print "More than one mods"
        record = records[0]
        metadata = {}
        metadata['title'] = self.getValuesForLabels(record, 'dc:title')[0]
        metadata['creator'] = self.getValuesForLabels(record, 'dc:creator')
        metadata['language'] = self.getValuesForLabels(record, 'dc:language')
        root = self._cdm.addNode(metadata=metadata, label=metadata['title']) 

        urls = self.getValuesForLabels(record, 'dc:identifier')
        i = 1
        for url in urls:
            parent = self._cdm.addNode(parent_id=root, label='[%d]' % i)
            self._cdm.addNode(parent_id=parent, url=url, sequenceNumber=i)
            i= i+1
        #self._cdm.printStructure()

    def getValuesForLabels(self, record, tag_name):
        res = []
        for data_field in record.getElementsByTagName(tag_name):
            res.append(data_field.firstChild.nodeValue.encode('utf-8'))
        return res
    
#class MarcParser(Parser):
#    def __init__(self):
#        Parser.__init__(self)
#    
#    def parse(self, root):
#        
#        records = root.getElementsByTagName('record')
#
#        # get the id number of the first record
#        if len(records) == 0:
#                print "No mods"
#        if len(records) > 1:
#                print "More than one mods"
#        record = records[0]
#        self._content['title'] = self._getFields(record, '245', 'a') 
#        self._content['urls'] = self._getFields(record, '856', 'u')
#            # loop through the control fields of the first record
#    def _getFields(self, record, tag, code):
#        values = []
#        for data_field in record.getElementsByTagName('datafield'):
#            if  data_field.hasAttributes() and \
#                data_field.getAttribute('tag') == tag:
#                for sub_field in data_field.getElementsByTagName('subfield'):
#                    if  sub_field.hasAttributes() and \
#                           sub_field.getAttribute('code') == code:
#                        values.append(sub_field.firstChild.nodeValue.encode('utf-8'))
#        return values
#        
#
#class ModsParser(Parser):
#    def __init__(self):
#        Parser.__init__(self)
#
#    def parse(self, root):
#        self._content = {
#            'title': [], 
#            'urls' : [], 
#        }
#        
#        records = root.getElementsByTagName('mods')
#
#        # get the id number of the first record
#        if len(records) == 0:
#                print "No mods"
#        if len(records) > 1:
#                print "More than one mods"
#        if records:
#            # loop through the control fields of the first record
#            for data_field in records[0].getElementsByTagName('titleInfo'):
#                for sub_field in data_field.getElementsByTagName('title'):
#                    self._content['title'].append(sub_field.firstChild.nodeValue.encode('utf-8'))
#            for data_field in records[0].getElementsByTagName('location'):
#                for sub_field in data_field.getElementsByTagName('url'):
#                    self._content['urls'].append(sub_field.firstChild.nodeValue.encode('utf-8'))


#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")


