# -*- coding: utf-8 -*-
from random import choice
import os
import subprocess
import urllib2
import shutil
import logging
import re
import codecs

from zc.buildout import UserError
import zc.recipe.egg
import setuptools

SCRIPT_TEMPLATE = {}
SCRIPT_TEMPLATE['wsgi'] = '''

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
  ]
%(initialization)s
import %(module_name)s

application = %(module_name)s.%(attrs)s(%(arguments)s)
'''
SCRIPT_TEMPLATE['fcgi'] = '''

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
  ]
%(initialization)s
import %(module_name)s

%(module_name)s.%(attrs)s(%(arguments)s)
'''

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.log = logging.getLogger(name)
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.name, self.options = buildout, name, options
        
        options['bin-directory'] = buildout['buildout']['bin-directory']

        options.setdefault('src-dir', self.buildout['buildout']['directory'])
        options.setdefault('project', 'project')
        options.setdefault('settings', '%s.settings' % options['project'])
        
        # Set this so the rest of the recipe can expect the values to be
        # there. We need to make sure that both pythonpath and extra-paths are
        # set for BBB.
        if 'extra-paths' in options:
            options['pythonpath'] = options['extra-paths']
        else:
            options.setdefault('extra-paths', options.get('pythonpath', ''))
        
        options.setdefault('control-script', self.name)
        
        options.setdefault('wsgi', 'false')
        options.setdefault('fcgi', 'false')
        options.setdefault('logfile', '')
        
        self.extra_paths = [
            os.path.join(buildout['buildout']['directory'], p.strip())
            for p in options.get('extra-paths', '').split('\n')
            if p.strip()
            ]
        if self.extra_paths:
            options['extra-paths'] = '\n'.join(self.extra_paths)
        

    def install(self):
        requirements, ws = self.egg.working_set(['djangoprojectrecipe'])
        
        # the list of files that are created by this recipe. buildout will
        # automatically delete these accordingly when the configuration has
        # changed or this recipe is uninstalled.
        script_paths = []
        
        # Create the Django management script
        script_paths.extend(self.create_manage_script(self.extra_paths, ws))

        # Make the wsgi and fastcgi scripts if enabled
        script_paths.extend(self.make_scripts(self.extra_paths, ws))
        
        return script_paths

    def update(self):
        return self.install()

    def create_manage_script(self, extra_paths, ws):
        # create the startscripts
        site_config=self.get_main_site_config()
        scripts = []
        scripts.extend(
            zc.buildout.easy_install.scripts(
                [(site_config['control-script'],
                  'djangoprojectrecipe.manage', 'main')],
                ws, self.options['executable'], self.options['bin-directory'],
                extra_paths = extra_paths,
                arguments= "'%s'" % (site_config['settings_module']))
        )
        return scripts


    def make_scripts(self, extra_paths, ws):
        site_config=self.get_main_site_config()
        scripts = []
        _script_template = zc.buildout.easy_install.script_template
        for protocol in ('wsgi', 'fcgi'):
            zc.buildout.easy_install.script_template = \
                zc.buildout.easy_install.script_header + \
                    SCRIPT_TEMPLATE[protocol]
            if self.options.get(protocol, '').lower() == 'true':
                scripts.extend(
                    zc.buildout.easy_install.scripts(
                        [('%s.%s' % (site_config['control-script'],
                                     protocol),
                          'djangoprojectrecipe.%s' % protocol, 'main')],
                        ws,
                        self.options['executable'],
                        self.options['bin-directory'],
                        extra_paths=extra_paths,
                        arguments= "'%s', logfile='%s'" % (
                            site_config['settings_module'],
                            self.options.get('logfile'))))
        zc.buildout.easy_install.script_template = _script_template
        return scripts

    def command(self, cmd, **kwargs):
        output = subprocess.PIPE
        if self.buildout['buildout'].get('verbosity'):
            output = None
        command = subprocess.Popen(
            cmd, shell=True, stdout=output, **kwargs)
        return command.wait()

    def create_file(self, file, template, options, overwrite=False):
        if not overwrite and os.path.exists(file):
            return

        f = open(file, 'w')
        f.write(template % options)
        f.close()
    
    def get_main_site_config(self):
        return {
            'site_name': None,
            'settings_module':'%s' % (self.options['settings'],),
            'control-script':'%s' % (self.options['control-script'],),
        }