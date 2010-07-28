#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Logging module for the Multivio application."""

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
from optparse import OptionParser

# local modules

import logging
from mvo_config import MVOConfig
from web_app import WebApplication

class LoggerError:
    """Base class for errors in the Logger packages."""
    class InvalidFileName(Exception):
        """The given file name is not correct."""
        pass

class Logger:
    """To log several messages"""
    def __init__(self, name="multivio", log_output_file=None, log_console=True,
                log_level=logging.DEBUG):
        """ Create an Looger object for messages logging.

            Keyword arguments:
                name  -- string : message application name
                log_output_file  -- string : name of the output file
                log_console  -- string : print message on the console
                log_level  -- logging.level : level of the log messages
        """
        self.name = name
        # create logger with "spam_application"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s"\
                                        "- %(message)s")
        # create file handler logger
        if log_output_file is not None:
            try:
                log_filehandler = logging.FileHandler(log_output_file)
            except IOError:
                raise LoggerError.InvalidFileName("Output file: %s cannot be " \
                        "created." % log_output_file)
            log_filehandler.setFormatter(formatter)
            self.logger.addHandler(log_filehandler)

        # create console handler logger
        if log_console is True:
            log_console = logging.StreamHandler()
            log_console.setLevel(log_level)
            log_console.setFormatter(formatter)
            self.logger.addHandler(log_console)

LOGGER = Logger(MVOConfig.Logger.name, MVOConfig.Logger.file_name,
                MVOConfig.Logger.console, MVOConfig.Logger.level)

class LoggerApp(WebApplication):
    """Web application for logging"""
    def __init__(self):
        """Basic constructor"""
        WebApplication.__init__(self)
        self.usage = """Using the POST method it put a log message in"\
                        "the server.<br>"""
        self.logger = logging.getLogger(MVOConfig.Logger.name + "."
                + self.__class__.__name__) 
    
    def post(self, environ, start_response):
        """Get the log message from the client in forward it into the loggging
        system of the server.
        """
        content = self.get_post_form(environ)
        body = content.value
        if isinstance(content.value, list):
            body = str(content.value)
        self.logger.info(body)
        start_response('200 OK', [('content-type', 'text/html')])
        return ["Ok"]


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
