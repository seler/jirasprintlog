===========
git jiralog
===========
Simple script that lists JIRA issues from specified sprint.
-----------------------------------------------------------

Installation
============

::

    cd path/to/pyframe/tools/jirasprintlog
    python -m pip install . --proxy http://10.71.16.7:8008

Dependencies
============

Script should work on both Python 2.7 and 3.*.

It relies on:

    * `jira <http://jira.readthedocs.io/en/latest/installation.html#dependencies>` which in turn depends on some other stuff and `pycrypto`.

    * `Jinja2 <http://jinja2.readthedocs.io/en/latest/>`


Setup
=====

Put config file in `~/gjl.ini`.

::

        [DEFAULT]
        JIRA_URL = http://webvrt59:8080
        JIRA_USER = USER123
        JIRA_PASS = Pass123

Usage
=====


::
   
    jira-sprint-log [-o <output file>]

Running tests
=============


::

    python setup.py test
