#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

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
import re
from xml.dom.minidom import parseString

# local modules
import logger
import logging
from mvo_config import MVOConfig
from web_app import WebApplication

from pdf_parser import PdfParser
from dc_parser import DublinCoreParser
from img_parser import ImgParser
from mets_parser import MetsParser
from marc_parser import MarcParser
import parser
from web_app import ApplicationError


#------------------ Classes ----------------------------
class DocParserApp(WebApplication):
    """ Parser chooser or selector.
        
        Based on the mime type it select the right chooser and return a vaild
        http response.
    """
    def __init__(self, temp_dir=MVOConfig.General.temp_dir):
        """ Build and instance used by the dispatcher.

         Keyword arguments:
            counter -- int: initial value for the node counter
            sequence_number -- int: initial value for the sequence number often
                                    usefull for parser of parsers
        """
        WebApplication.__init__(self, temp_dir)


        self.usage = """ Using the GET method it return the metadata, the
        logical structure and the physical structure in json format.<br>
<h2>Arguments:</h2>
<ul> 
    <li><em>url --string--</em>  url of a xml/pdf file representing the record.  
</ul> 
<h2>Examples:</h2>

<h3>GetMetadata:</h3>
<ul> 
<li><a href="/server/metadata/get?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/server/metadata/get?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/server/metadata/get?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<h4>Examples Mets:</h4>
<ul> 
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/server/metadata/get?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<h4>Examples Pdf:</h4>
<ul> 
<li><a href="/server/metadata/get?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>

<h3>GetLogicalStructure:</h3>
<ul> 
<li><a href="/server/structure/get_logical?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/server/structure/get_logical?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/server/structure/get_logical?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<h4>Examples Mets:</h4>
<ul> 
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/server/structure/get_logical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<h4>Examples Pdf:</h4>
<ul> 
<li><a href="/server/structure/get_logical?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>

<h3>GetPhysicalStructure:</h3>
<ul> 
<li><a href="/server/structure/get_physical?url=http://doc.rero.ch/record/9264/export/xd?"><b>Simple Dublin Core.</b></a>
<li><a
href="/server/structure/get_physical?url=http://doc.rero.ch/lm.php?url=1000,40,6,20091106095458-OI/2009INFO006.pdf"><b>Simple Pdf.</b></a>
<li><a
href="/server/structure/get_physical?url=http://doc.rero.ch/record/12703/export/xd?"><b>Dublin
Core with Pdfs inside..</b></a>
</ul>

<h4>Examples Mets:</h4>
<ul> 
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN338271201"><b>DFG Example 110 pages, 4 labels+titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574578609"><b>DFG Example: 165 pages, 26 labels + titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN243574339"><b>DFG Example: 421 pages, 71 labels + titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN326329617"><b>DFG Example: 15 pages, 3 labels + titre, fichier rattaché au root.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN58460422X"><b>DFG Example: 172 pages, 4 labels + titre.</b></a>
<li><a href="/server/structure/get_physical?url=http://gdz.sub.uni-goettingen.de/mets_export.php?PPN=PPN574841571"><b>DFG Example: 276 pages, 24 labels + titre.</b></a>
</ul>
<h4>Examples Pdf:</h4>
<ul> 
<li><a href="/server/structure/get_physical?url=http://doc.rero.ch/lm.php?url=1000,40,4,20091104141001-BU/Th_FautschC.pdf"><b>PDF with TOC.</b></a>
</ul>
"""
    
    def get(self, environ, start_response):
        """ Callback method for new http request.
        
        """
        #get parameters from the URI
        (path, opts) = self.getParams(environ)

        #check if is valid
        self.logger.debug("Accessing: %s with opts: %s" % (path, opts))

        if re.search(r'metadata/get', path) is not None:
            self.logger.debug("Get Metadata with opts: %s" % opts)
            if opts.has_key('url'):
                try:
                    metadata = self.getMetaData(opts['url'])
                except Exception:
                    start_response('400 Bad Request', [('content-type',
                           'text/html')])
                    return ["Invalid arguments."]
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % metadata]

        if re.search(r'structure/get_logical', path) is not None:
            self.logger.debug("Get Logical with opts: %s" % opts)
            if opts.has_key('url'):
                try:
                    logical = self.getLogicalStructure(opts['url'])
                except Exception:
                    start_response('400 Bad Request', [('content-type',
                           'text/html')])
                    return ["Invalid arguments."]
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % logical]

        if re.search(r'structure/get_physical', path) is not None:
            self.logger.debug("Get Physical with opts: %s" % opts)
            if opts.has_key('url'):
                try:
                    physical = self.getPhysicalStructure(opts['url'])
                except Exception:
                    start_response('400 Bad Request', [('content-type',
                           'text/html')])
                    return ["Invalid arguments."]
                start_response('200 OK', [('content-type',
                    'application/json')])
                return ["%s" % physical]

        start_response('400 Bad Request', [('content-type', 'text/html')])
        return ["Invalid arguments."]

    def _chooseParser(self, content, url, mime):

        if re.match('.*?/pdf.*?', mime):
            self.logger.debug("Pdf parser found!")
            return PdfParser(content, url, url.split('/')[-1])
        
        if re.match('image/.*?', mime):
            self.logger.debug("Image parser found!")
            return ImgParser(content, url, mime)

        if re.match('.*?/xml.*?', mime):
            #some METS files contain uppercase mets directive
            self.logger.debug("XML parser found!")
            content_str = content.read()
            content.seek(0)
            content_str = content_str.replace('METS=', 'mets=')
            content_str = content_str.replace('METS:', 'mets:')
            content_str = content_str.replace('MODS=', 'mods=')
            content_str = content_str.replace('MODS:', 'mods:')
            doc = parseString(content_str)
            
            #METS parser
            selected_parser = None
            try:
                self.logger.debug("Try Mets parser!")
                selected_parser = MetsParser(content, url)
                self.logger.debug("Mets parser found!")
            except parser.ParserError.InvalidDocument:
                self.logger.debug('Cannot be parsed by Mets parser')
            try:
                self.logger.debug("Try DC parser!")
                selected_parser = DublinCoreParser(content, url)
                self.logger.debug("DubinCore parser found!")
            except parser.ParserError.InvalidDocument:
                self.logger.debug('Cannot be parsed by DC parser')

            try:
                self.logger.debug("Try Marc parser!")
                selected_parser = MarcParser(content, url)
                self.logger.debug("Marc parser found!")
            except parser.ParserError.InvalidDocument:
                self.logger.debug('Cannot be parsed by Marc parser')

            return selected_parser

    def getMetaData(self, url):
        (local_file, mime) = self.getRemoteFile(url)
            
        content = file(local_file,'r')

        #check the mime type
        self.logger.debug("Url: %s Detected Mime: %s" % (url, mime))
        parser = self._chooseParser(content, url, mime)
        metadata = parser.getMetaData()
        metadata['mime'] = mime
            
        return json.dumps(metadata,  sort_keys=True, indent=2)

    def getLogicalStructure(self, url):
        (local_file, mime) = self.getRemoteFile(url)
        content = file(local_file,'r')

        #check the mime type
        self.logger.debug("Url: %s Detected Mime: %s" % (url, mime))
        parser = self._chooseParser(content, url, mime)
        logic = parser.getLogicalStructure()
        #logic['mime'] = mime
            
        return json.dumps(logic,  sort_keys=True, indent=2)

    def getPhysicalStructure(self, url):
        (local_file, mime) = self.getRemoteFile(url)
        content = file(local_file,'r')

        #check the mime type
        self.logger.debug("Url: %s Detected Mime: %s" % (url, mime))
        parser = self._chooseParser(content, url, mime)
        physic = parser.getPhysicalStructure()
        #physic['mime'] = mime
            
        return json.dumps(physic,  sort_keys=True, indent=2)

    def getParams(self, environ):
        """ Overload the default method to allow cgi url.
            
            The url parameter should be at the end of the url.
            i.e.
            /server/structure/get_logical?format=raw&url=http:www.toto.ch/test?url=http://www.test.ch
            is ok, but:
            /server/structure/get_logical?url=http:www.toto.ch/test?url=http://www.test.ch&format=raw
            is incorrect.
        """
        path = environ['PATH_INFO']
        opts = {}
        to_parse = environ['QUERY_STRING']
        if len(to_parse) > 0:
            res = list(re.match(r'[(.*?)&]{0,1}url=(.*)', to_parse).groups())
            #replace all until the first occurence of url=
            opts['url'] = res.pop()
            if len(res) > 0:
                for v in res:
                    args = v.split('&')
                    for a in args:
                        res_args = list(re.match(r'(.*?)=(.*)', a).groups())
                        opts[res_args[0]] = res_args[1]
                    
        return (path, opts)

            
    
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
    application = DocParserApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()

