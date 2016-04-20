#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Simple config file for Multivio server."""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================


import logging

class MVOConfig:

    class General:
        temp_dir = '/tmp'
        lib_dir = '/var/www/multivio/lib/python'
        sys_pathes = ['/var/www/multivio/lib/python',
                '/var/www/mutlivio/bin']

    class Url:
        user_agent = 'Firefox/3.5.2'
        timeout = 120 #2 minutes

    class Logger:
        name = "multivio"
        file_name = "/tmp/multivio.log"
        console = True
        level = logging.DEBUG
