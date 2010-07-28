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
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from xml.dom.minidom import parseString

# local modules
from parser import DocumentParser, ParserError

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
        dc_dc = doc.getElementsByTagName('dc:dc')
        if len(dc_dc) and dc_dc[0].namespaceURI == \
            'http://purl.org/dc/elements/1.1/':
            return True
        return False

    def _get_record(self):
        """Get the record in the xml file."""
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        doc = parseString(content_str)
        
        records = doc.getElementsByTagName('collection')

        # get the id number of the first record
        if len(records) == 0:
            raise ParserError.InvalidDocument(
                "XML/Dublin Core document should contains at lease one record!")
        if len(records) > 1:
            raise ParserError.InvalidDocument(
                "XML/Dublin Core document should not contains more than "\
                "one record!")
        return records[0]

    def get_metadata(self):
        """Get pdf infos."""
        record = self._get_record()
        metadata = {}
        metadata['title'] = self._get_values_for_labels(record,
                'dc:title')[0].decode('utf-8')
        metadata['creator'] = [v.decode('utf-8') for v in
            self._get_values_for_labels(record, 'dc:creator')]
        metadata['language'] = self._get_values_for_labels(record,
                'dc:language')[0].decode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self._get_record()
        urls = self._get_values_for_labels(record, 'dc:identifier')
        for url in urls:
            phys_struct.append({
                'url': url,
                'label': url.split('/')[-1]
            })
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct


    def _get_values_for_labels(self, record, tag_name):
        """Return the value for a xml label."""
        res = []
        for data_field in record.getElementsByTagName(tag_name):
            if data_field.firstChild is not None:
                res.append(data_field.firstChild.nodeValue.encode('utf-8'))
        return res

