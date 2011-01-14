#!/usr/bin/python
# -*- coding: utf-8 -*-

""" RERO config file for Multivio server."""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

import logging
import re

def get_internal_file(url):
    """Get the file in local."""
    document_type = {
            '10' : 'book',
            '20' : 'journal', 
            '25' : 'newspaper',
            '30' : 'picture', 
            '40' : 'thesis',
            '41' : 'dissertation',
            '42' : 'preprint',
            '43' : 'postprint',
            '44' : 'report',
            '15' : 'partition'
            }
    localisations = {
            '1'  : 'rero',
            '2'  : 'unifr',
            '3'  : 'unige',
            '4'  : 'unine',
            '5'  : 'unil',
            '6'  : 'unisi',
            '8'  : 'hetsfr',
            '9'  : 'hegge',
            '10' : 'ecav',
            '11' : 'hevs2',
            '12' : 'hepvs',
            '13' : 'iukb',
            '14' : 'idiap',
            '15' : 'fsch',
            '16' : 'cred',
            '17' : 'curpufm',
            '18' : 'crem',
            '19' : 'medvs',
            '20' : 'crepa',
            '21' : 'ffhs',
            '22' : 'hevs_',
            '23' : 'bpuge',
            '24' : 'hetsge',
            '25' : 'baage',
            '26' : 'elsvd',
            '28' : 'hedsfr',
            '29' : 'bvcfne',
            '30' : 'coege',
            '31' : 'mhnge',
            '32' : 'bpune',
            '33' : 'bcufr',
            '34' : 'bmuge',
            '35' : 'imvge',
            '36' : 'aege',
            '37' : 'avlvd',
            '38' : 'cio',
            '39' : 'pa16ju',
            '40' : 'iheid'
            }

    journal_collections = {
            '4'  : 'cahiers_de_psychologie',
            '5'  : 'dossiers_de_psychologie',
            '6'  : 'droit_du_bail',
            '7'  : 'revue_suisse_droit_sante',
            '10' : 'bulletin_vals_asla',
            '13' : 'revue_tranel'
    }
            
    newspaper_collections = {
            '1'  : 'la_liberte',
            '2'  : 'freiburger_nachrichten',
            '8'  : 'la_pilule',
            '9'  : 'le_cretin_des_alpes',
            '11' : 'messager_boiteux_neuchatel',
            '12' : 'revue_historique_neuchateloise',
            '13' : 'etrennes_fribourgeoises',
            '14' : 'rameau_de_sapin',
            '15' : 'l_express',
            '16' : 'l_impartial',
            '17' : 'bulletin_sng',
            '18' : 'federation_horlogere',
            '19' : 'bibliotheques_et_musees'
    }

    mime = 'unknown'
    local_file = None
    if re.match('http://doc.rero.ch/lm.php', url):
        parts = url.split(',')
        if parts[0].endswith('1000'):
            doc_type = document_type[parts[1]]
            if doc_type == 'journal':
                collection = journal_collections[parts[2]]
            elif doc_type == 'newspaper':
                collection = newspaper_collections[parts[2]]
            else:
                collection = localisations[parts[2]]
            local_file = '/rerodoc/public/%s/%s/%s' \
                % (doc_type, collection, parts[3])
            if re.match(".*?\.(pdf)", local_file):
                mime = "application/pdf"
            if re.match(".*?\.(jpg|jpeg)", local_file):
                mime = "image/jpeg"
            if re.match(".*?\.png", local_file):
                mime = "image/png"
            if re.match(".*?\.gif", local_file):
                mime = "image/gif"
        else:
            from multivio.web_app import ApplicationError
            raise ApplicationError.PermissionDenied(
                "Your are not allowed to see this document.")
    return (mime, local_file)

class MVOConfig:
    """Main class for configuration."""

    class General:
        """General config."""
        temp_dir = '/var/tmp/multivio' 
        lib_dir = '/rero/multivio/lib/python'
        sys_pathes = ['/rero/multivio/lib/python',
                '/www/mutlivio-test/bin']

    class Url:
        """Configuration for uploads."""
        user_agent = 'Firefox/3.5.2'
        timeout = 120 #2 minutes

    class Logger:
        """Config for logging."""
        name = "multivio"
        file_name = "/var/log/multivio/multivio.log"
        console = False
        level = logging.INFO
