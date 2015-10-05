    # coding=utf-8
"""
Profiler utility for python
Active8 (04-03-15)
license: GNU-GPL2
"""

from setuptools import setup
setup(name='cmdssh',
      version='49',
      description='Execute commands on local machine and on remote machine via ssh, and a wrapper for paramikos scp.',
      url='https://github.com/erikdejonge/cmdssh',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      packages=['cmdssh'],
      zip_safe=True,
      install_requires=['requests', 'paramiko', 'consoleprinter', 'arguments', 'pytz'],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta ",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: POSIX",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Terminals",
          "Topic :: System",
      ])
