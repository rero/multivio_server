#!/usr/bin/python
"""Config file for multivio server."""
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


import logging
import re


def get_internal_file(url, force=False):
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
            '19' : 'bibliotheques_et_musees',
            '20' : 'depeche_de_neuchatel'
    }

    mime = 'unknown'
    local_file = None
    if re.match('http://doc.rero.ch/lm.php', url):
        parts = url.split(',')
        if force or parts[0].endswith('1000'):
            doc_type = document_type[parts[1]]
            if doc_type == 'journal':
                collection = journal_collections[parts[2]]
            elif doc_type == 'newspaper':
                collection = newspaper_collections[parts[2]]
            else:
                collection = localisations[parts[2]]
            local_file = '/rerodoc/public/%s/%s/%s' \
                % (doc_type, collection, parts[3])
            if re.match(".*?\.(pdf)", local_file.lower()):
                mime = "application/pdf"
            if re.match(".*?\.(jpg|jpeg)", local_file.lower()):
                mime = "image/jpeg"
            if re.match(".*?\.(tif|tiff)", local_file.lower()):
                mime = "image/tiff"
            if re.match(".*?\.png", local_file.lower()):
                mime = "image/png"
            if re.match(".*?\.gif", local_file.lower()):
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
        temp_dir = '/reroweb/var/tmp/multivio' 
        lib_dir = '/reroweb/var/scripts/multivio/lib/python'
        sys_pathes = ['/reroweb/var/scripts/multivio/lib/python',
            '/reroweb/var/www/mutlivio/bin']
    class Security:
        pdf_max_width = 100
        pdf_max_height = 100
        img_max_width = 100
        img_max_height = 100

    class Url:
        """Configuration for uploads."""
        user_agent = 'Firefox/3.5.2'
        timeout = 120 #2 minutes

    class Logger:
        """Config for logging."""
        name = "multivio"
        file_name = "/tmp/multivio.log"
        console = False
        level = logging.DEBUG
