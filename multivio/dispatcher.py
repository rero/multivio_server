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

from wsgiref.util import setup_testing_defaults
import cgi
import json
#import simplejson as json
import datetime
# third party modules
import logger
import parser
import thumb
import pdf
import re

class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read

class Dispatcher(object):
    def __init__(self):
        self._logger = logger.Logger('/tmp/multivio.log')
        self._parser = parser.ParserSelector()
        self._thumb = thumb.Thumb()
        self._pdf = pdf.PdfConverter()
        self.usage = """<br><h1>Welcome to the multivio server.</h1>
<h2>Available pathes:</h2>
    <h3>/multivio/document/get?url=</h3>
        Using the GET method it return a CDM in json format.<br>
        <b>Arguments:</b>
        <ul>
        <li><em>url --string--</em>  url of a xml file representing the record.
        </ul>
        <a
        href="/multivio/document/get?url=http://doc.rero.ch/record/9264/export/xd?"><b>RERODOC
        example.</b></a>
    <h3>/multivio/log</h3>
        Using the POST method it put a log message in the server.<br>
    <h3>/multivio/document/thumbnail?size=400&url=</h3>
        Using the GET method it return a thumbnail in PNG format of a given size for a given
        image.<br>
        <b>Arguments:</b>
        <ul>
        <li><em>url --string--</em>  url of an image file.
        <li><em>size --integer--</em>  size of the output image in pixel.
        </ul>
        <a
        <a
        href="/multivio/document/thumbnail?size=400&url=http://doc.rero.ch/lm.php?url=1000,10,2,20080701134109-FH/Braune_MWK_tab1a.jpg"><b>Thumbnail
        example.</b></a>
    <h3>/multivio/document/pdf?zoom=1&pagenr=1&url=</h3>
        Using the GET method it return a PNG image corresponding to the pagenr
        of pdf document for a given zoom factor.<br>
        <ul>
        <li><em>url --string--</em>  url of a pdf file.
        <li><em>zoom --real--</em>  zoom factor for the output image file.
        <li><em>pagenr --integer--</em>  page number of the input pdf file to
        convert.
        </ul>
        <a
        href="/multivio/document/pdf?pagenr=1&zoom=2&url=http://doc.rero.ch/lm.php?url=1000,43,2,20091211165357-BU/shalkevitch_rfg.pdf"><b>PDF
        example.</b></a>
    <h3>/multivio/document/html?zoom=1&pagenr=1&url=</h3>
        Using the GET method it return a html document corresponding to the pagenr
        of pdf document for a given zoom factor.<br>
        <ul>
        <li><em>url --string--</em>  url of a pdf file.
        <li><em>zoom --real--</em>  zoom factor for the output image file.
        <li><em>pagenr --integer--</em>  page number of the input pdf file to
        convert.
        </ul>
        <a href="/multivio/document/html?pagenr=1&zoom=2&url=http://doc.rero.ch/lm.php?url=1000,43,2,20091211165357-BU/shalkevitch_rfg.pdf"><b>HTML
        example.</b></a>
"""
        
    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        print path
        opts = cgi.parse_qs(environ['QUERY_STRING'])
        if re.match('.*?/log', path):
            if self.isPostRequest(environ):
                content = self.getPostForm(environ)
                json_body = content.value
                now = datetime.datetime.now()
                header = '%s - - [%s] "POST %s/%s %s"'\
                    % (environ.get('SERVER_NAME'),
                    now, path, opts, environ.get('SERVER_PROTOCOL')
                    )
                self._logger.addLog(header, json_body)
                start_response('200 OK', [('content-type', 'text/html')])
                return ["Ok"]
            else:
                start_response('405 Method Not Allowed', [('content-type', 'text/html')])
                return ["Only Post Options is allowed."]

        if re.match('.*?/document/get', path):
            if not self.isPostRequest(environ):
                if opts.has_key('url'):
                    doc = self._parser.parseUrl(opts['url'][0]) 
                    print doc.json()
                    start_response('200 OK', [('content-type',
                        'application/json')])
                    return ["%s" % doc.json()]
                else:
                    start_response('400 Bad Request', [('content-type', 'text/html')])
                    return ["Missing url options."]
                    
            else:
                start_response('405 Method Not Allowed', [('content-type', 'text/html')])
                return ["Only Post Options is allowed."]

        if re.match('.*?/document/thumbnail', path):
            if not self.isPostRequest(environ):
                if opts.has_key('url'):
                    size = 100
                    if opts.has_key('size'):
                        size = opts['size'][0]
                    (header, content) = self._thumb.generate(opts['url'][0], size)
                    start_response('200 OK', header)
                    return [content]
                else:
                    start_response('400 Bad Request', [('content-type', 'text/html')])
                    return ["Missing url options."]
                    
            else:
                start_response('405 Method Not Allowed', [('content-type', 'text/html')])
                return ["Only Post Options is allowed."]
        
        if re.match('.*?/document/pdf', path):
            if not self.isPostRequest(environ):
                if opts.has_key('url'):
                    pagenr = 1
                    zoom = 1.0
                    if opts.has_key('zoom'):
                        zoom = float(opts['zoom'][0])
                    if opts.has_key('pagenr'):
                        pagenr = int(opts['pagenr'][0])
                    (header, content) = self._pdf.getPng(opts['url'][0],
                        pagenr=pagenr, zoom=zoom)
                    start_response('200 OK', header)
                    return [content]
                else:
                    start_response('400 Bad Request', [('content-type', 'text/html')])
                    return ["Missing url options."]
                    
            else:
                start_response('405 Method Not Allowed', [('content-type', 'text/html')])
                return ["Only Post Options is allowed."]
        
        if re.match('.*?/document/html', path):
            if not self.isPostRequest(environ):
                if opts.has_key('url'):
                    pagenr = 1
                    if opts.has_key('pagenr'):
                        pagenr = int(opts['pagenr'][0])
                    zoom = 1.0
                    if opts.has_key('zoom'):
                        zoom = float(opts['zoom'][0])
                    (header, content) = self._pdf.getHtml(opts['url'][0],
                        pagenr=pagenr, zoom=zoom)
                    start_response('200 OK', header)
                    return [content]
                else:
                    start_response('400 Bad Request', [('content-type', 'text/html')])
                    return ["Missing url options."]
                    
            else:
                start_response('405 Method Not Allowed', [('content-type', 'text/html')])
                return ["Only Post Options is allowed."]
        print "Not found!"
        start_response('404 Not Found', [('content-type', 'text/html')])

        return ["%s" % self.usage]
        
    def isPostRequest(self, environ):
        if environ['REQUEST_METHOD'].upper() != 'POST' and\
            environ['REQUEST_METHOD'].upper() != 'OPTIONS':
            return False
        else:
            return True
        content_type = environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
        #return (content_type.startswith('application/x-www-form-urlencoded' or content_type.startswith('multipart/form-data')))
    
    def getPostForm(self, environ):
        input = environ['wsgi.input']
        post_form = environ.get('wsgi.post_form')
        if (post_form is not None
            and post_form[0] is input):
            return post_form[2]
        fs = cgi.FieldStorage(fp=input,
                              environ=environ,
                              keep_blank_values=1)
        new_input = InputProcessed()
        post_form = (new_input, input, fs)
        environ['wsgi.post_form'] = post_form
        environ['wsgi.input'] = new_input
        return fs

application = Dispatcher()

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
    from wsgiref.simple_server import make_server
    #server = make_server('localhost', 8081, simple_app)
    server = make_server('', 4041, application)
    server.serve_forever()


