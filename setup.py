import os

from setuptools import setup, find_packages

version = '0.9.0'

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__),
                             name)).read()

readme = read_file('README')
changes = read_file('HISTORY')

setup(name='djangoprojectrecipe',
      version=version,
      description="Buildout recipe for Django - the divio branch",
      long_description='\n\n'.join([readme, changes]),
      classifiers=[
        'Framework :: Buildout',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        ],
      package_dir={'': 'src'},
      packages=find_packages('src'),
      keywords='',
      author='Stefan Foulis',
      author_email='stefan.foulis@gmail.com',
      url='http://github.com/stefanfoulis/djangorecipe',
      license='BSD',
      zip_safe=False,
      install_requires=[
        'zc.buildout',
        'zc.recipe.egg',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = djangoprojectrecipe.recipe:Recipe
      """,
      )
