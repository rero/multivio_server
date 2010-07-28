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
        if len(marc) and marc[0].namespaceURI == \
            'http://www.loc.gov/MARC21/slim':
            return True
        return False

    def _get_record(self):
        """Get the record object in the xml file."""
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        doc = parseString(content_str)
        
        records = doc.getElementsByTagName('record')

        # get the id number of the first record
        if len(records) == 0:
            raise ParserError.InvalidDocument(
                "XML/Marc Core document should contains at lease one record!")
        if len(records) > 1:
            raise ParserError.InvalidDocument(
                "XML/Marc Core document should not contains more than "\
                "one record!")
        return records[0]

    def get_metadata(self):
        """Get pdf infos."""
        record = self._get_record()
        metadata = {}
        metadata['title'] = self._get_fields(record, tag='245',
            code='a')[0].decode('utf-8')
        metadata['creator'] = [v.decode('utf-8') for v in
            self._get_fields(record, tag='100', code='a')]
        metadata['creator'].extend([v.decode('utf-8') for v in
            self._get_fields(record, tag='700', code='a')])
        metadata['language'] = self._get_fields(record, tag='041',
            code='a')[0].decode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self._get_record()
        urls = self._get_fields(record, tag='856', code='u')
        labels = self._get_fields(record, tag='856', code='z')
        if len(urls) != len(labels):
            self.logger.warning('Length of labels is different that urls!')
        for i in range(len(urls)):
            phys_struct.append({
                'url': urls[i].decode('utf-8'),
                'label': labels[i].decode('utf-8')
            })
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct


    def _get_fields(self, record, tag, code):
        """Get fields content given the tag name."""
        values = []
        for data_field in record.getElementsByTagName('datafield'):
            if data_field.hasAttributes() and \
                data_field.getAttribute('tag') == tag:
                for sub_field in data_field.getElementsByTagName('subfield'):
                    if sub_field.hasAttributes() and \
                           sub_field.getAttribute('code') == code:
                        values.append(
                            sub_field.firstChild.nodeValue.encode('utf-8'))
        return values


