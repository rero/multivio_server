#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Multivio HTTP requests dispatcher."""

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import re
from optparse import OptionParser

# third party modules
import logger
import logging
#import mvo_parser
import processor
import parser_app
import version_app

from web_app import WebApplication
from mvo_config import MVOConfig


class DispatcherApp(WebApplication):
    """ Dispach http request to several applications given the URI.
    
        This is the entry point of the server application. This class is
        responsible to call applications given the URI of the HTTP request.
    """

    def __init__(self):
        "Simple constructor." 
        
        WebApplication.__init__(self)

        #application configuration
        self._apps = {}
        #Client logger
        self._apps['.*?/log/post'] = logger.LoggerApp()
        self._apps['.*?/version'] = version_app.VersionApp()
        self._apps['.*?/get'] = \
            parser_app.DocParserApp(temp_dir=MVOConfig.General.temp_dir)
        self._apps['.*?/document/get'] = \
            processor.DocumentApp(temp_dir=MVOConfig.General.temp_dir)
        self.usage = """<br><h1>Welcome to the multivio server.</h1><br>"""
        self.logger = logging.getLogger(MVOConfig.Logger.name+".Dispatcher")
        
    def __call__(self, environ, start_response):
        """Main method to dispatch HTTP requests."""

        (path, opts) = self.getParams(environ)
        self.logger.debug("Request: %s", path)
        if re.match('.*?/help', path) or len(path) == 0:
            start_response('200 OK', [('content-type', 'text/html')])
            response = [self.usage]
            response.extend(["<h2>Available pathes:</h2>"])
            for k in self._apps.keys():
                response.extend(["<h3>%s</h3>" % k])
                self.logger.debug(self._apps[k].usage)
                response.extend([self._apps[k].usage])
            return response
        for k in self._apps.keys():
            if re.match(k, path):
                return self._apps[k](environ, start_response)
        else:
            start_response('404 File Not Found', [('content-type',
                            'text/html')])
            return ["Invalid URL."]


#---------------------------- Main Part ---------------------------------------

def main():
    """Main function"""

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Web app to test the dispatcher.")

    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)

    (options, args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")
    from wsgiref.simple_server import make_server
    application = DispatcherApp()
    server = make_server('', options.port, application)
    server.serve_forever()

if __name__ == '__main__':
    main()