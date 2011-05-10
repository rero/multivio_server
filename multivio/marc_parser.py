#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

__copyright__ = "Copyright (c) 2009-2011 RERO"
__license__ = "GPL V.2"

#---------------------------- Modules ---------------------------------------

# import of standard modules
import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from xml.dom.minidom import parseString

import re

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
        self._namespace_URI = 'http://www.loc.gov/MARC21/slim'
        try:
            doc = parseString(content_str)
        except Exception:
            return False
        marc = doc.getElementsByTagNameNS(self._namespace_URI, 'collection')
        if len(marc):
            return True
        return False

    def _get_record(self):
        """Get the record object in the xml file."""
        self._file_stream.seek(0)
        content_str = self._file_stream.read()
        doc = parseString(content_str)
        
        records = doc.getElementsByTagNameNS(self._namespace_URI, 'record')

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
        lang =  self._get_fields(record, tag='041', code='a')
        if len(lang) == 1:
            metadata['language'] = lang[0].decode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self._get_record()
        urls = self._get_fields(record, tag='856', code='u')
        labels = self._get_fields(record, tag='856', code='z')
        if len(labels) == 0:
            for u in urls:
                labels.append(re.sub(r'\.\w+$','',u.split('/')[-1]))
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
        for data_field in record.getElementsByTagNameNS(self._namespace_URI, 'datafield'):
            if data_field.hasAttributes() and \
                data_field.getAttribute('tag') == tag:
                for sub_field in data_field.getElementsByTagNameNS(self._namespace_URI, 'subfield'):
                    if sub_field.hasAttributes() and \
                           sub_field.getAttribute('code') == code:
                        values.append(
                            sub_field.firstChild.nodeValue.encode('utf-8'))
        return values


