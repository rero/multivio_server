#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

import sys
sys.stdout = sys.stderr

import os

#mvo_config.py is in the same directory than the main wsgi application
script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)
from mvo_config import MVOConfig

#library location
[sys.path.insert(0,p) for p in MVOConfig.General.sys_pathes]


import multivio.dispatcher_app

application = multivio.dispatcher_app.DispatcherApp()

