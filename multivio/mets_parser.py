#!/usr/bin/env python
"""Document Parser module for Multivio"""
# -*- coding: utf-8 -*-

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
from optparse import OptionParser
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from xml.dom.minidom import parseString
import re

# local modules
from parser import DocumentParser, ParserError

#----------------------------------- Classes -----------------------------------

class MetsParser(DocumentParser):
    """To parse PDF document"""

    def __init__(self, file_stream, url):
        DocumentParser.__init__(self, file_stream)
        self._url = url

        #read the content of the file
        self._content_str = self._file_stream.read()
        
        self._logical_structure = None
        self._physical_structure = None
        self._meta_data = None
        self._relation = None
        self._file_list = None

        #some METS files contain uppercase mets directive
        self._content_str = self._content_str.replace('METS=', 'mets=')
        self._content_str = self._content_str.replace('METS:', 'mets:')
        self._content_str = self._content_str.replace('MODS=', 'mods=')
        self._content_str = self._content_str.replace('MODS:', 'mods:')
        try:
            self._doc = parseString(self._content_str)
        except Exception:
            raise ParserError.InvalidDocument("The file is invalid. (is it" \
                    "corrupted?)")
        if self._check_xml() is not True:
            raise ParserError.InvalidDocument("The file is invalid. (is it" \
                    "corrupted?)")
        
        

    def _check_xml(self):
        """Check if the pdf is valid."""
        #METS parser
        mets = self._doc.getElementsByTagName('mets:mets')
        if len(mets) > 0 and re.match('http://www.loc.gov/METS',
                mets[0].namespaceURI):
            return True
        return False

    def get_metadata(self):
        """Get pdf infos."""
        metadata = {}
        self._get_logical_structure(self._doc)
        self._get_metadata(self._doc)
        
        logical_nodes = self._logical_structure.keys()
        logical_nodes.sort()
        dmd_id = self._logical_structure[logical_nodes[0]]['dmd_id']
        metadata = {}
        metadata['title'] = self._meta_data[dmd_id]['title']
        metadata['creator'] = self._meta_data[dmd_id]['creator']
        metadata['language'] = self._meta_data[dmd_id]['language']

        self.logger.debug("Metadata: %s"% json.dumps(metadata, sort_keys=True, 
                        indent=4))
        return metadata
    
    def get_logical_structure(self):
        """Get the logical structure of the Mets."""
        self._get_logical_structure(self._doc)
        self._get_physical_structure(self._doc)
        self._get_file_list(self._doc)
        self._get_physical_logical(self._doc)
        #logical_struct = {}
        
        def get_parts(logic_struct):
            to_return = []
            nodes = logic_struct.keys()
            nodes.sort()
            for node in nodes:
                url = None
                self.logger.debug('Node: %s', logic_struct[node]['id'])
                if self._relation.has_key(logic_struct[node]['id']):
                    phys_id = self._relation[logic_struct[node]['id']][0]
                    for _file in self._physical_structure[phys_id]['files']:
                        if self._file_list.has_key(_file):
                            url = self._file_list[_file]
                to_return.append({
                    'label' : logic_struct[node]['label'],
                    'file_position' : {
                        'index' : None,
                        'url'   : url
                    }
                })
                if logic_struct[node].has_key('child'):
                    to_return[-1]['childs'] = \
                        get_parts(logic_struct[node]['child'])
            return to_return

        #print self._logical_structure
        if self._logical_structure[1].has_key('child'):
            logical_struct = get_parts(self._logical_structure[1]['child'])
        else:
            return None
        self.logger.debug("Logical Structure: %s"% json.dumps(logical_struct,
                sort_keys=True, indent=4))
        #self.logger.debug("Physical Structure: %s"%
        #json.dumps(self._physical_structure,
        #        sort_keys=True, indent=4))
        #self.logger.debug("Phys2Log Structure: %s"%
        #json.dumps(self._relation,
        #        sort_keys=True, indent=4))
        #self.logger.debug("FileList Structure: %s"% json.dumps(self._file_list,
        #        sort_keys=True, indent=4))
        return logical_struct
    
    def get_physical_structure(self):
        """Get the physical structure of the pdf."""
        self._get_physical_structure(self._doc)
        self._get_file_list(self._doc)
        phys_struct = []
        keys = self._physical_structure.keys()
        def phys_cmd(val1, val2):
            """Comparison method for sorting physical struct based on ORDER
                field
            """
            if not self._physical_structure.has_key(val1):
                return -1
            if not self._physical_structure.has_key(val2):
                return +1
            return cmp(self._physical_structure[val1]['order'],
                    self._physical_structure[val2]['order'])
        keys.sort(phys_cmd)
        for k in keys:
            for f in self._physical_structure[k]['files']:
                if self._file_list.has_key(f):
                    phys_struct.append({
                      'url':  self._file_list[f],
                      'label':
                        self._file_list[f].split('/')[-1]
                    })
        self.logger.debug("Physical Structure: %s"% json.dumps(phys_struct,
                sort_keys=True, indent=4))
        return phys_struct

    def _get_metadata(self, node):
        """Parse admin part of the METS to retrieve metadata."""
        self._meta_data = {}
        dmd_sec = node.getElementsByTagName('mets:dmdSec')
        for s in dmd_sec:
            _id = s.getAttribute('ID')
            self._meta_data[_id] = {}
            md_wrap = s.getElementsByTagName('mets:mdWrap')
            self._meta_data[_id]['title'] = ""
            for m in md_wrap:
                if m.hasAttributes() and m.getAttribute('MDTYPE') == 'MODS':
                    title_info = m.getElementsByTagName('mods:titleInfo')
                    if len(title_info) > 0:
                        title = title_info[0].getElementsByTagName('mods:title')
                        if len(title) > 0:
                            self._meta_data[_id]['title'] = \
                                title[0].firstChild.nodeValue.encode('utf-8')

                    language = m.getElementsByTagName('mods:language')
                    self._meta_data[_id]['language'] = ""
                    if len(language) > 0:
                        language_term = \
                          language[0].getElementsByTagName('mods:languageTerm')
                        if len(language_term) > 0:
                            self._meta_data[_id]['language'] = \
                              language_term[0].firstChild.nodeValue.encode('utf-8')

                    name = m.getElementsByTagName('mods:name')
                    self._meta_data[_id]['creator'] = []
                    for n in name:
                        role = n.getElementsByTagName('mods:role')
                        if len(role) < 1 or \
                          role[0].getElementsByTagName('mods:roleTerm')[0].firstChild.nodeValue.encode('utf-8') == 'aut':
                            name_part = n.getElementsByTagName('mods:namePart')
                            first_name = ""
                            last_name = ""
                            for np in name_part:
                                if not np.hasAttributes():
                                    complete_name = \
                                      np.firstChild.nodeValue.encode('utf-8')
                                    self._meta_data[_id]['creator'].append(
                                      "%s" % complete_name)
                                if np.getAttribute('type') == 'family':
                                    last_name = \
                                      np.firstChild.nodeValue.encode('utf-8')
                                if np.getAttribute('type') == 'given':
                                    first_name = \
                                      np.firstChild.nodeValue.encode('utf-8')
                                if last_name and first_name:
                                    self._meta_data[_id]['creator'].append(
                                      "%s, %s" % (last_name, first_name))
            

    def _get_logical_structure(self, node):
        self._logical_structure = {}
        n = 1
        struct_map = node.getElementsByTagName('mets:structMap')
        for sm in struct_map:
            if sm.hasAttributes() and \
              sm.getAttribute('TYPE') == 'LOGICAL':
                self._logical_structure = self._get_logical_nodes(sm, n)
                return

    def _get_logical_nodes(self, node, n):
        to_return = {}
        div = node.childNodes
        #print len(div)
        for d in div:
            if d.localName == 'div':
                order = n
                if len(d.getAttribute('ID')) > 0:
                    _id = d.getAttribute('ID')
                    dmd_id = None
                    if len(d.getAttribute('ORDER')) > 0:
                        order = int(d.getAttribute('ORDER'))
                    else:
                        n = n + 1

                    if len(d.getAttribute('DMDID')) > 0:
                        dmd_id = d.getAttribute('DMDID')
                    label = ""
                    if len(d.getAttribute('LABEL')) > 0:
                        label = d.getAttribute('LABEL')
                    else:
                        if len(d.getAttribute('TYPE')) > 0:
                            label = d.getAttribute('TYPE')
                    mptrs = d.getElementsByTagName('mets:mptr')
                    external_docs = []
                    for m in mptrs:
                        url = m.getAttribute('xlink:href')
                        external_docs.append(url)
                    to_return[order] = {
                        'label' : label,
                        'id' : _id,
                        'dmd_id' : dmd_id,
                        'external_docs' : external_docs
                        }
                child_node = self._get_logical_nodes(d, n)
                if to_return.has_key(order):
                    if len(child_node) > 0:
                        to_return[order]['child'] = child_node
                else:
                    to_return = child_node
        return to_return
    
    def _get_physical_structure(self, node):
        self._physical_structure = {}
        n = 0
        struct_map = node.getElementsByTagName('mets:structMap')
        for sm in struct_map:
            if sm.hasAttributes() and \
                    sm.getAttribute('TYPE') == 'PHYSICAL':
                div = sm.getElementsByTagName('mets:div')
                for d in div:
                    if d.getAttribute('TYPE') == 'physSequence':
                        sub_div = d.getElementsByTagName('mets:div')
                        for sd in sub_div:
                            if len(sd.getAttribute('ORDER')) > 0:
                                order = int(sd.getAttribute('ORDER'))
                            else:
                                n = n + 1
                                order = n
                            if len(sd.getAttribute('ID')) > 0:
                                _id = sd.getAttribute('ID')
                            files = []
                            f_ptr = sd.getElementsByTagName('mets:fptr')
                            for f in f_ptr:
                                files.append(f.getAttribute('FILEID'))
                            self._physical_structure[_id] = {
                                'order' : order,
                                'files' : files
                            }

    def _get_file_list(self, node):
        self._file_list = {}
        file_sec = node.getElementsByTagName('mets:fileSec')
        for fs in file_sec:
            file_grp = fs.getElementsByTagName('mets:fileGrp')
            for fg in file_grp:
                if fg.hasAttributes() and fg.getAttribute('USE') == 'DEFAULT':
                    files = fg.getElementsByTagName('mets:file')
                    for f in files:
                        _id = f.getAttribute('ID')
                        f_locat = f.getElementsByTagName('mets:FLocat')
                        self._file_list[_id] = \
                          f_locat[0].getAttribute('xlink:href')
    
    def _get_physical_logical(self, node):
        self._relation = {}
        struct_link = node.getElementsByTagName('mets:structLink')
        for sl in struct_link:
            sm_link = sl.getElementsByTagName('mets:smLink')
            for sm in sm_link:
                x_from = sm.getAttribute('xlink:from')
                x_to = sm.getAttribute('xlink:to')
                if not self._relation.has_key(x_from):
                    self._relation[x_from] = []
                self._relation[x_from].append(x_to)


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

