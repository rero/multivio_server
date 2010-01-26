#!/usr/bin/python

# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

import sys
sys.stdout = sys.stderr

import multivio

config = {
    'temp_data_dir': '/www/multivio/temp',
    'log_dir': '/www/multivio/log'
}
application = multivio.Dispatcher(config=config)
