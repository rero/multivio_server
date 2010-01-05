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

# third party modules
import logger
import parser
import document
#import thumb
#import pdf
import re
from application import Application


class Dispatcher(Application):
    def __init__(self):
        self._apps = {}
        self._apps['/multivio/log/post'] = logger.LoggerApp('/tmp/multivio.log')
        self._apps['/multivio/cdm/get'] = parser.CdmParserApp()
        self._apps['/multivio/document/get'] = document.DocumentApp()
        self.usage = """<br><h1>Welcome to the multivio server.</h1><br>"""
        
    def __call__(self, environ, start_response):
        (path, opts) = self.getParams(environ)
        if re.match('.*?/help', path) or re.match('.*?/multivio$', path):
            start_response('200 OK', [('content-type', 'text/html')])
            response = [self.usage]
            response.extend(["<h2>Available pathes:</h2>"])
            for k in self._apps.keys():
                response.extend(["<h3>%s</h3>" % k])
                print self._apps[k].usage
                response.extend([self._apps[k].usage])
            return response
        for k in self._apps.keys():
            if re.match(k, path):
                return self._apps[k](environ, start_response)
        else:
            start_response('404 File Not Found', [('content-type', 'text/html')])
            return ["Invalid URL."]

        #if re.match('.*?/log/post', path):
        #    return self._logger_app(environ, start_response)

        #if re.match('.*?/cdm/get', path):
        #    return self._cdm_app(environ, start_response)
        #
        #if re.match('.*?/document/get', path):
        #    return self._document_app(environ, start_response)

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


