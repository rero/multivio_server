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
import cgi
import re
import datetime

# third party modules
from application import Application



class LoggerApp(Application):
    def __init__(self):
        Application.__init__(self)
        self.usage = """Using the POST method it put a log message in the server.<br>"""
    
    def post(self, environ, start_response):
        (path, opts) = self.getParams(environ)
        content = self.getPostForm(environ)
        body = content.value
        if isinstance(content.value, list):
            body = str(content.value)
        now = datetime.datetime.today()
        header = '%s - - [%s] "POST %s/%s %s"'\
            % (environ.get('SERVER_NAME'),
            now, path, opts, environ.get('SERVER_PROTOCOL')
            )
        self.addLog(header, body)
        start_response('200 OK', [('content-type', 'text/html')])
        return ["Ok"]

    def addLog(self, header, body):
        print header
        print body


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


    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")
    from wsgiref.simple_server import make_server
    application = LoggerApp('/tmp/multivio.log')
    server = make_server('', options.port, application)
    server.serve_forever()


