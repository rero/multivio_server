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

class MarcParser(DocumentParser):
    """To parse XMLMarc document"""

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
        marc = doc.getElementsByTagName('collection')
        if len(marc) and marc[0].namespaceURI == 'http://www.loc.gov/MARC21/slim':
            return True
        return False

    def getRecord(self):
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        doc = parseString(content_str)
        
        records = doc.getElementsByTagName('record')

        # get the id number of the first record
        if len(records) == 0:
                raise PaserError.InvalidDublinCore("XML/Marc Core document should contains at lease one record!")
        if len(records) > 1:
                raise PaserError.InvalidDublinCore("XML/Marc Core document should not contains more than one record!")
        return records[0]

    def getMetaData(self):
        """Get pdf infos."""
        record = self.getRecord()
        metadata = {}
        metadata['title'] = self.getFields(record, tag='245', code='a')[0].decode('utf-8')
        metadata['creator'] = [v.decode('utf-8') for v in
            self.getFields(record, tag='100', code='a')]
        metadata['creator'].extend([v.decode('utf-8') for v in
            self.getFields(record, tag='700', code='a')])
        metadata['language'] = self.getFields(record, tag='041', code='a')[0].decode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def getPhysicalStructure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self.getRecord()
        urls = self.getFields(record, tag='856', code='u')
        labels = self.getFields(record, tag='856', code='z')
        if len(urls) != len(labels):
            self.logger.debug('Length of labels is different that urls!')
        for i in range(len(urls)):
            phys_struct.append({
                'url': urls[i].decode('utf-8'),
                'label': labels[i].decode('utf-8')
            })
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct


    def getFields(self, record, tag, code):
        values = []
        for data_field in record.getElementsByTagName('datafield'):
            if  data_field.hasAttributes() and \
                data_field.getAttribute('tag') == tag:
                for sub_field in data_field.getElementsByTagName('subfield'):
                    if  sub_field.hasAttributes() and \
                           sub_field.getAttribute('code') == code:
                        values.append(sub_field.firstChild.nodeValue.encode('utf-8'))
        return values

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

