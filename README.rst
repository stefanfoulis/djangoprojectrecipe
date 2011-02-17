===================
djangoprojectrecipe
===================

This buildout recipe can be used to create the necessary commands to replace
``manage.py`` in a buildout environment. Optionally it can also generate 
scripts for wsgi and fcgi.

simple example::

  [buildout]
  parts = django
  eggs = 
      django

  [django]
  recipe = djangoprojectrecipe
  settings = myproject.settings
  eggs = ${buildout:eggs}
  extra-paths = src
  project = myproject


Supported options
=================

The recipe supports the following options.

``project``
  This option sets the name for your project package.

``settings``
  You can set the name of the settings file which is to be used with
  this option. This is useful if you want to have a different
  production setup from your development setup. It defaults to
  ``project.settings``.

``extra-paths``
  All paths specified here will be used to extend the default Python
  path for the `bin/*` scripts. It is recommended to define these directly
  in the ``[buildout]`` section and juste reference them. See the examples.

``control-script``
  The name of the script created in the bin folder. This script is the
  equivalent of the ``manage.py`` Django normally creates. By default it
  uses the name of the section (the part between the ``[ ]``).

``wsgi``
  An extra script is generated in the bin folder when this is set to
  ``true``. This can be used with mod_wsgi to deploy the project. The
  name of the script is ``control-script.wsgi``.

``fcgi``
  Like ``wsgi`` this creates an extra script within the bin folder. This
  script can be used with an FCGI deployment.

``logfile``
  In case the WSGI server you're using does not allow printing to stdout,
  you can set this variable to a filesystem path - all stdout/stderr data
  is redirected to the log instead of printed. The same logfile will be used
  for fcgi. You can use the base directory for relative paths:
  ``logfile = ${buildout:directory}/log/django.log``


FCGI specific settings
======================

Options for FCGI can be set within a settings file (``settings.py``). The options
is ``FCGI_OPTIONS``. It should be set to a dictionary. The part below is an
example::

  FCGI_OPTIONS = {
      'method': 'threaded',
  }


Another example
===============

The next example shows you how to use some more of the options. Here we seperate
out ``eggs`` and ``extra-paths`` onto the buildout configuration and use it both in
a part to get a general python interpreter and a django instance with the
same paths::

  [buildout]
  versions=versions
  parts = 
      python
      django
  eggs =
    django
    South
    django-cms
  extra-paths = 
      src
      ../external_apps/
      /some/other/directory/to/add/to/pythonpath/
      parts/django_svn/django/
  
  [versions]
  django = 1.2.4
  
  [python]
  recipe = zc.recipe.egg
  interpreter = python
  eggs = ${buildout:eggs}
  extra-paths = ${buildout:extra-paths}
  scripts =
      python
  
  [django]
  recipe = djangoprojectrecipe
  settings = myproject.settings_live
  wsgi = true
  eggs = ${buildout:eggs}
  extra-paths = ${buildout:extra-paths}


Using django trunk
==================

``djangoprojectrecipe`` does not handle installing django at all. The easiest 
case is when installing released versions from pypi (just add ``django`` to 
``eggs``). If you want to use django trunk or some special branch, 
`infrae.subversion` may be of service::

  [buildout]
  versions=versions
  develop = 
      parts/svn/django/
  parts = 
      svn
      django
  eggs = 
      django
      South
      django-whatever
  
  [versions]
  django=
  
  [svn]
  recipe = infrae.subversion
  urls = http://code.djangoproject.com/svn/django/trunk/
  
  [django]
  recipe = djangoprojectrecipe
  settings = myproject.settings_dev
  eggs = ${buildout:eggs}
  extra-paths = ${buildout:extra-paths}

Don't forget to add `svn` to `parts` and `parts/svn/django/` to
`develop`. Also you should remove the specific version setting from `[versions]`
for django, because otherwise buildout will continue to use the packaged 
version.

See http://pypi.python.org/pypi/infrae.subversion for more examples.


Example configuration for mod_wsgi
==================================

If you want to deploy a project using mod_wsgi you could use this
example as a starting point::

  <Directory /path/to/buildout>
         Order deny,allow
         Allow from all
  </Directory>
  <VirtualHost 1.2.3.4:80>
         ServerName      my.rocking.server
         CustomLog       /var/log/apache2/my.rocking.server/access.log combined
         ErrorLog        /var/log/apache2/my.rocking.server/error.log
         WSGIScriptAlias / /path/to/buildout/bin/django.wsgi
  </VirtualHost>
