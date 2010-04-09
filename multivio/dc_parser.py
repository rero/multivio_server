#!/usr/bin/env python
"""Document Parser module for Multivio"""
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules ---------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser
import pyPdf
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from xml.dom.minidom import parseString

# local modules
from parser import DocumentParser

#----------------------------------- Classes -----------------------------------

class DublinCoreParser(DocumentParser):
    """To parse PDF document"""

    def __init__(self, file_stream, url):
        DocumentParser.__init__(self, file_stream)
        self._url = url

    def _check(self):
        """Check if the pdf is valid."""
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        try:
            doc = parseString(content_str)
        except Exception:
            return False
        dc = doc.getElementsByTagName('dc:dc')
        if len(dc) and dc[0].namespaceURI == 'http://purl.org/dc/elements/1.1/':
            return True
        return False

    def getRecord(self):
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        doc = parseString(content_str)
        
        records = doc.getElementsByTagName('collection')

        # get the id number of the first record
        if len(records) == 0:
                raise PaserError.InvalidDublinCore("XML/Dublin Core document should contains at lease one record!")
        if len(records) > 1:
                raise PaserError.InvalidDublinCore("XML/Dublin Core document should not contains more than one record!")
        return records[0]

    def getMetaData(self):
        """Get pdf infos."""
        record = self.getRecord()
        metadata = {}
        metadata['title'] = self.getValuesForLabels(record,
                'dc:title')[0].decode('utf-8')
        metadata['creator'] = [v.decode('utf-8') for v in self.getValuesForLabels(record,
                'dc:creator')]
        metadata['language'] = self.getValuesForLabels(record,
                'dc:language')[0].decode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def getPhysicalStructure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self.getRecord()
        urls = self.getValuesForLabels(record, 'dc:identifier')
        for url in urls:
            phys_struct.append({
                'url': url,
                'label': url.split('/')[-1]
            })
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct


    def getValuesForLabels(self, record, tag_name):
        res = []
        for data_field in record.getElementsByTagName(tag_name):
            if data_field.firstChild is not None:
                res.append(data_field.firstChild.nodeValue.encode('utf-8'))
        return res

#---------------------------- Main Part ---------------------------------------
def main():
    """Main function"""
    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("To test the Logger class.")

    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")

    from wsgiref.simple_server import make_server
    application = LoggerApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()

