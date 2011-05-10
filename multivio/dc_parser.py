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

# local modules
from parser import DocumentParser, ParserError

#----------------------------------- Classes -----------------------------------

class DublinCoreParser(DocumentParser):
    """To parse PDF document"""

    def __init__(self, file_stream, url):
        self._namespace_URI = 'http://purl.org/dc/elements/1.1/'
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
        dc_dc = doc.getElementsByTagNameNS(self._namespace_URI, 'dc')
        if len(dc_dc):
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
                'title')[0].decode('utf-8')
        metadata['creator'] = [v.decode('utf-8') for v in
            self._get_values_for_labels(record, 'creator')]
        metadata['language'] = self._get_values_for_labels(record,
                'language')[0].decode('utf-8')
        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        phys_struct = []
        record = self._get_record()
        urls = self._get_values_for_labels(record, 'identifier')
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
        for data_field in record.getElementsByTagNameNS(self._namespace_URI, tag_name):
            if data_field.firstChild is not None:
                res.append(data_field.firstChild.nodeValue.encode('utf-8'))
        return res

