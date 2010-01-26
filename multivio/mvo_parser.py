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
import hashlib
import urllib
import pyPdf
from application import Application
import re
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
#import simplejson as json

# third party modules


# local modules
import cdm

class CdmParserApp(Application):
    def __init__(self, counter=1, sequence_number=1, temp_dir=None):
        Application.__init__(self, temp_dir)
        #self._mods = ModsParser()
        #self._marc = MarcParser()
        self._pdf = TocPdfParser(counter=counter, sequence_number=sequence_number)
        self._meds = MedsParser(counter=counter, sequence_number=sequence_number)
        self._dc = DublinCoreParser(counter=counter, sequence_number=sequence_number)
        self._img = ImageParser(counter=counter, sequence_number=sequence_number)
        self.usage = """ Using the GET method it return a CDM in json format.<br>
<b>Arguments:</b>
<ul> 
    <li><em>url --string--</em>  url of a xml file representing the record.  
</ul> 
<b>Examples:</b>
<ul> 
<li><a href="/multivio/cdm/get?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/multivio/cdm/get?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/multivio/cdm/get?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<b>Examples Mets:</b>
<ul> 
<li><a href="/multivio/cdm/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/multivio/cdm/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/multivio/cdm/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/multivio/cdm/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/multivio/cdm/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/multivio/cdm/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<b>Examples Pdf:</b>
<ul> 
<li><a href="/multivio/cdm/get?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>
"""
    
    def get(self, environ, start_response):
        (path, opts) = self.getParams(environ)
        if opts.has_key('url'):
            url = opts['url'][0]
            #url = urllib.unquote(opts['url'][0])
            self._dc.reset()
            self._pdf.reset()
            self._img.reset()
            try:
                doc = self.parseUrl(url) 
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % doc.json()]
            except Exception:
                start_response('200 OK', [('content-type',
                    'application/json')])
                err = ErrorParser('Error during Parsing')
                return ["%s" % err.json()]
                
        else:
            start_response('400 Bad Request', [('content-type', 'text/html')])
            return ["Missing url options."]

    def parseFile(self, file_name):
        f = file(file_name)
        content = f.read()
        f.close()
        return self._parse(content)
    
    def getParams(self, environ):
        path = environ['PATH_INFO']
        opts = {}
        to_parse = environ['QUERY_STRING']
        if len(to_parse) > 0:
            opts['url'] = [to_parse.replace('url=','', 1)]
        return (path, opts)

    def parseUrl(self, query_url):
        (local_file, mime) = self.getRemoteFile(query_url)
        content = file(local_file,'r')
        if re.match('.*?/pdf.*?', mime):
            self._pdf.parse(content, query_url)
            return self._pdf
        if re.match('.*?image/.*?', mime):
            self._img.parse(query_url)
            return self._img
        print "Url: %s Detected Mime: %s" % (query_url, mime)
        if re.match('.*?/xml.*?', mime):
            return self._parseXml(content)

    def _parseXml(self, content):
        #self._dc = DublinCoreParser()
        content_str = content.read()
        content_str = content_str.replace('METS=', 'mets=')
        content_str = content_str.replace('METS:', 'mets:')
        content_str = content_str.replace('MODS=', 'mods=')
        content_str = content_str.replace('MODS:', 'mods:')
        doc = parseString(content_str)
        #root = doc.documentElement
        mets = doc.getElementsByTagName('mets:mets')
        if len(mets) > 0 and re.match('http://www.loc.gov/METS',
                mets[0].namespaceURI):
            self._meds.parse(doc)
            return self._meds
    
        dc = doc.getElementsByTagName('dc:dc')
        if len(dc) and dc[0].namespaceURI == 'http://purl.org/dc/elements/1.1/':
            self._dc.parse(doc, temp_dir=self._tmp_dir)
            return self._dc
        print "Error: no valid parser detected for !"
            
    

class Parser:
    def __init__(self, counter=1, sequence_number=1):
        self._cdm = cdm.CoreDocumentModel(counter=counter)
        self._sequence_number = sequence_number

    def reset(self):
        self._cdm = cdm.CoreDocumentModel(counter=1)
        self._sequence_number = 1
    
    def json(self):
        return json.dumps(self._cdm, sort_keys=True, indent=4, encoding='utf-8')
        #return json.dumps(self._cdm)
        
    def display(self):
        print self.json()


class TocPdfParser(Parser, pyPdf.PdfFileReader):
    def __init__(self, counter=1, sequence_number=1):
        Parser.__init__(self, counter=counter, sequence_number=sequence_number)

        self._physical_to_logical = None
        self._local_sequence_number = 1
    
    def __initpdf__(self, stream):
        pyPdf.PdfFileReader.__init__(self, stream)

        def _setup_page_id_to_num(pages=None, _result=None, _num_pages=None):
            if _result is None:
                _result = {}
            if pages is None:
                _num_pages = []
                pages = self.trailer["/Root"].getObject()["/Pages"].getObject()
            t = pages["/Type"]
            if t == "/Pages":
                for page in pages["/Kids"]:
                    #if len(_num_pages) == 0:
                        #_num_pages.append(1)
                    _result[page.idnum] = len(_num_pages) + 1
                    _setup_page_id_to_num(page.getObject(), _result, _num_pages)
            else:
                if t == "/Page":
                    _num_pages.append(1)
            return _result
        self._page_id_to_page_numbers = _setup_page_id_to_num()

    def getPageNumber(self, title):
        return self._page_id_to_page_numbers.get(page_idnum, '???')

    def displayToc(self):
        print "Title: %s" % self.getDocumentInfo().title
        print "Author: %s" % self.getDocumentInfo().author
        print "Number of pages: %s" % self.getNumPages()
        res = {}
        def print_part(data, space=' '):
            for obj in data:
                if isinstance(obj, pyPdf.pdf.Destination):
                    print "%s%s %s" %(space, obj.title,
                        self._page_id_to_page_numbers.get(obj.page.idnum, '???'))
                elif isinstance(obj, list):
                    print_part(obj, space + "  ")
        print_part(self.getOutlines())
    
    def getMetaData(self, query_url):
        metadata = {}
        info = None
        try:
            info = self.getDocumentInfo()
        except:
            pass
        if info and info.title is not None and self.hasToc():
            metadata['title'] = self.getDocumentInfo().title
        else:
            metadata['title'] = 'PDF Document'
            pdf_file_parts = query_url.split('/')
            if len(pdf_file_parts) > 0:
                if re.match('.*?\.pdf', pdf_file_parts[-1]):
                    metadata['title'] = pdf_file_parts[-1]

        if info and info.author is not None:
            metadata['creator'] = [self.getDocumentInfo().author]
        else:
            metadata['creator'] = ['unknown']
        metadata['language'] = ['unknown']
        return metadata

    def parse(self, stream, query_url):
        self.__initpdf__(stream)
        metadata = self.getMetaData(query_url)
        root = self._cdm.addNode(metadata=metadata, label=metadata['title']) 
        self._physical_to_logical = {1:[root]}
        def get_parts(data, parent_id):
            for obj in data:
                if isinstance(obj, pyPdf.pdf.Destination):
                    label = obj.title
                    pagenr = self._page_id_to_page_numbers.get(obj.page.idnum, '???')
                    current = self._cdm.addNode(parent_id=parent_id, label=label)
                    if not self._physical_to_logical.has_key(pagenr):
                        self._physical_to_logical[pagenr] = []
                    self._physical_to_logical[pagenr].append(current)
                elif isinstance(obj, list):
                    get_parts(obj, current)
        outlines = self.getOutlines()
        if self.hasToc() :
            get_parts(self.getOutlines(), root)
            self.appendPages(query_url)
        else:
            for i in range(self.getNumPages()):
                self._cdm.addNode(url=urllib.quote(query_url),
                    sequenceNumber=self._sequence_number+i,
                    localSequenceNumber=i+1,
                    parent_id=root)
        self._sequence_number = self._sequence_number + self.getNumPages()
        self._local_sequence_number = self._local_sequence_number + self.getNumPages()

    def hasToc(self):
        for obj in self.getOutlines():
            if isinstance(obj, pyPdf.pdf.Destination):
                return True
        return False
    
    def appendPages(self, query_url):
        pages = self._physical_to_logical.keys()
        pages.sort()
        n_pages = self.getNumPages()
        for i, p in enumerate(pages):
            _from = p
            _to = n_pages+1
            if i < len(pages) -1:
                _to = pages[i+1]
            if len(self._physical_to_logical[p][:-1]) > 0:
                self._cdm.addNode(url=urllib.quote(query_url),
                    sequenceNumber=p+self._sequence_number - 1, localSequenceNumber=p,
                    parent_id=self._physical_to_logical[p])
                _from = _from + 1
            for i in range(_from, _to):
                self._cdm.addNode(url=urllib.quote(query_url),
                    sequenceNumber=self._sequence_number + i - 1,
                    localSequenceNumber=i,
                    parent_id=self._physical_to_logical[p][-1])

    
class ErrorParser(Parser):
    def __init__(self, msg="Error", counter=1, sequence_number=1):
        Parser.__init__(self, counter=-1, sequence_number=sequence_number)
        metadata = {'title':msg,
                    'creator' : ['Server'],
                    'language' : ['en']
        }
        self._cdm.addNode(metadata=metadata, label=metadata['title']) 

class ImageParser(Parser):
    def __init__(self, counter=1, sequence_number=1):
        Parser.__init__(self, counter=counter, sequence_number=sequence_number)

    def parse(self, url):
        self._cdm.addNode(url=urllib.quote(url),
            sequenceNumber=self._sequence_number)
        if self._sequence_number is not None:
            self._sequence_number = self._sequence_number + 1

class DublinCoreParser(Parser):
    def __init__(self, counter=1, sequence_number=1):
        Parser.__init__(self, counter=counter, sequence_number=sequence_number)
    
    def parse(self, root, temp_dir):
        
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
        parent_id = self._cdm._node_name % (self._cdm._counter - 1)
        for url in urls:
            children_id = self._cdm._node_name % (self._cdm._counter)
            parser_chooser = CdmParserApp(counter=self._cdm._counter,
                sequence_number=self._sequence_number, temp_dir=temp_dir)
            sub_parser = parser_chooser.parseUrl(url)
            if sub_parser is not None:
                self._cdm._counter = sub_parser._cdm._counter
                self._cdm.update(sub_parser._cdm)
                if not self._cdm[parent_id].has_key('children'):
                    self._cdm[parent_id]['children'] = []
                self._cdm[parent_id]['children'].append(children_id)
                self._cdm[children_id]['parentId'] = parent_id
                self._sequence_number = sub_parser._sequence_number
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
class MedsParser(Parser):
    def __init__(self, counter=1, sequence_number=1):
        Parser.__init__(self, counter=counter, sequence_number=sequence_number)
        self._logical_structure = None
        self._physical_structure = None
        self._meta_data = None
        self._relation = None
        self._file_list = None
        self._physical_to_logical = None

    def parse(self, root):
        self.getLogicalStructure(root)
        self.getPhysicalStructure(root)
        self.getMetaData(root)
        self.getFileList(root)
        self.getRelationBetweenPhysicalAndLogical(root)
        #self.connectLogicalStructure()
        print self._logical_structure
        
        logical_nodes = self._logical_structure.keys()
        logical_nodes.sort()
        dmd_id = self._logical_structure[logical_nodes[0]]['dmd_id']
        metadata = {}
        metadata['title'] = self._meta_data[dmd_id]['title']
        metadata['creator'] = self._meta_data[dmd_id]['creator']
        metadata['language'] = self._meta_data[dmd_id]['language']
        #metadata['creator'] = logical_struct[logical_nodes[0]]['creator']
        #metadata['language'] = logical_struct[logical_nodes[0]]['language']
        cdm_root = self._cdm.addNode(metadata=metadata, label=metadata['title']) 
        #        
        current = self._logical_structure[logical_nodes[0]]
        self._physical_to_logical = {}
        if self._relation.has_key(current['id']):
            for f in self._relation[current['id']]:
                self._physical_to_logical[f] = [cdm_root]
        self.appendChild(cdm_root, self._logical_structure[logical_nodes[0]])
        #if self._logical_structure[logical_nodes[0]].has_key('files'):
        #    self.addFiles(cdm_root,
        #        self._logical_structure[logical_nodes[0]]['files'])
        #print self._physical_to_logical
        self.addFiles(cdm_root)
    
    def addFiles(self, cdm_root):
        keys = self._physical_to_logical.keys()
        def phys_cmd(x,y):
            if not self._physical_structure.has_key(x):
                return -1
            if not self._physical_structure.has_key(y):
                return +1
            return cmp(self._physical_structure[x]['order'], self._physical_structure[y]['order'])
        keys.sort(phys_cmd)
        #print keys
        for f in keys:
            if  self._physical_structure.has_key(f):
                file_ids = self._physical_structure[f]['files'] 
                for fi in file_ids:
                    if self._file_list.has_key(fi):
                        url = self._file_list[fi]
                sequence_number = self._physical_structure[f]['order']
                self._cdm.addNode(url=urllib.quote(url),
                    sequenceNumber=sequence_number,
                    parent_id=self._physical_to_logical[f])

            
        

    def appendChild(self, cdm_node, logical_struct):
        if not logical_struct.has_key('child'):
            return
        nodes = logical_struct['child'].keys()
        nodes.sort()
        childs = logical_struct['child']
        for n in nodes:
            current = childs[n]
            cdm_root =  self._cdm.addNode(parent_id=cdm_node, label=childs[n]['label']) 
            if self._relation.has_key(current['id']):
                for f in self._relation[current['id']]:
                    if not self._physical_to_logical.has_key(f):
                        self._physical_to_logical[f] = []
                    self._physical_to_logical[f].append(cdm_root)
                    #try:
                    self._physical_to_logical[f].remove(cdm_node)
                    #except:
                    #    pass
            self.appendChild(cdm_root, childs[n])
            #self.addFiles(cdm_root, childs[n]['files'])
        #for n in logical_nodes[1:]:
            
    
    def getMetaData(self, node):
        self._meta_data = {}
        dmd_sec = node.getElementsByTagName('mets:dmdSec')
        for s in dmd_sec:
            id = s.getAttribute('ID')
            self._meta_data[id] = {}
            md_wrap = s.getElementsByTagName('mets:mdWrap')
            self._meta_data[id]['title'] = ""
            for m in md_wrap:
                if m.hasAttributes() and m.getAttribute('MDTYPE') == 'MODS':
                    title_info = m.getElementsByTagName('mods:titleInfo')
                    if len(title_info) > 0:
                        title = title_info[0].getElementsByTagName('mods:title')
                        if len(title) > 0:
                            self._meta_data[id]['title'] = title[0].firstChild.nodeValue.encode('utf-8')

                    language = m.getElementsByTagName('mods:language')
                    self._meta_data[id]['language'] = []
                    if len(language) > 0:
                        language_term = language[0].getElementsByTagName('mods:languageTerm')
                        if len(language_term) > 0:
                            self._meta_data[id]['language'].append(language_term[0].firstChild.nodeValue.encode('utf-8'))

                    name = m.getElementsByTagName('mods:name')
                    self._meta_data[id]['creator'] = []
                    for n in name:
                        role = n.getElementsByTagName('mods:role')
                        if len(role) < 1 or role[0].getElementsByTagName('mods:roleTerm')[0].firstChild.nodeValue.encode('utf-8') == 'aut':
                            name_part = n.getElementsByTagName('mods:namePart')
                            first_name = ""
                            last_name = ""
                            for np in name_part:
                                if np.getAttribute('type') == 'family':
                                    last_name = np.firstChild.nodeValue.encode('utf-8')
                                if np.getAttribute('type') == 'given':
                                    first_name = np.firstChild.nodeValue.encode('utf-8')
                            self._meta_data[id]['creator'].append("%s, %s" % (last_name,
                                    first_name))
            

    def getLogicalStructure(self, node):
        self._logical_structure = {}
        n = 1
        struct_map = node.getElementsByTagName('mets:structMap')
        for sm in struct_map:
            if sm.hasAttributes() and \
                    sm.getAttribute('TYPE') == 'LOGICAL':
                        self._logical_structure = self.getLogicalNodes(sm, n)
                        return

    def getLogicalNodes(self, node, n):
        to_return = {}
        div = node.childNodes
        #print len(div)
        for d in div:
            if d.localName == 'div':
                order = n
                if len(d.getAttribute('ID')) > 0:
                    id = d.getAttribute('ID')
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
                    to_return[order] = {
                        'label' : label,
                        'id' : id,
                        'dmd_id' : dmd_id
                        }
                child_node = self.getLogicalNodes(d, n)
                if to_return.has_key(order):
                    if len(child_node) > 0:
                        to_return[order]['child'] = child_node
                else:
                    to_return = child_node
        return to_return
    
    def getPhysicalStructure(self, node):
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
                                id = sd.getAttribute('ID')
                            files = []
                            f_ptr = sd.getElementsByTagName('mets:fptr')
                            for f in f_ptr:
                                files.append(f.getAttribute('FILEID'))
                            self._physical_structure[id] = {
                                'order' : order,
                                'files' : files
                            }

    def getFileList(self, node):
        self._file_list = {}
        file_sec = node.getElementsByTagName('mets:fileSec')
        for fs in file_sec:
            file_grp = fs.getElementsByTagName('mets:fileGrp')
            for fg in file_grp:
                if fg.hasAttributes() and fg.getAttribute('USE') == 'DEFAULT':
                    files = fg.getElementsByTagName('mets:file')
                    for f in files:
                        id = f.getAttribute('ID')
                        f_locat = f.getElementsByTagName('mets:FLocat')
                        self._file_list[id] = f_locat[0].getAttribute('xlink:href')
    
    def getRelationBetweenPhysicalAndLogical(self, node):
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


if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)
    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)


    (options,args) = parser.parse_args ()

    if len(args) != 1:
        parser.error("Error: incorrect number of arguments, try --help")
    #from wsgiref.simple_server import make_server
    #application = CdmParserApp()
    #server = make_server('', options.port, application)
    #server.serve_forever()
    pdf_file_name = args[0]
    parser = TocPdfParser()
    parser.parse(stream=file(pdf_file_name), query_url=pdf_file_name)
    parser.displayToc()


