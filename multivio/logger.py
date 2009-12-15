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
import json
#import simplejson as json

# third party modules


# local modules
class LoggerError:
    class InvalidJsonFormat(Exception):
        pass
    class InvalidLogFile(Exception):
        pass

class Logger:
    def __init__(self, file_name):
        try:
            self._file = file(file_name, "a")
        except Exception:
            raise  LoggerError.InvalidLogFile("Cannot open file for writing %s" % file_name)
    
    def addLog(self, header, json_body):
        content = json_body #json.loads(json_body)
        self._file.write(header+"\n")
        self._file.write(json.dumps(content, sort_keys=True, indent=4)+"\n")
        self._file.flush()


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


