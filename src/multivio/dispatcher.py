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
import datetime
# third party modules
import logger
import parser
import thumb

class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read

class Dispatcher(object):
    def __init__(self):
        self._logger = logger.Logger('/tmp/multivio.log')
        self._parser = parser.ParserSelector()
        self._thumb = thumb.Thumb()
        
    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        print path
        opts = cgi.parse_qs(environ['QUERY_STRING'])
        if path == '/multivio/log':
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
        if path == '/multivio/document/get':
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

        if path == '/multivio/document/thumbnail':
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
        print "Not found!"
        start_response('404 Not Found', [('content-type', 'text/html')])

        return ["Page not found!"]
        
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
    server = make_server('localhost', 4041, application)
    server.serve_forever()


