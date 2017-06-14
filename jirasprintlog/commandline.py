import os
import sys
import argparse
import configparser

from jirasprintlog import JiraSprintLoggerError, JiraSprintLogger
from jirasprintlog import __doc__ as description
from jirasprintlog import __version__ as version


_CONFIG_FILENAME = 'gjl.ini'
CONFIG_FILENAME = os.path.expanduser(os.path.join('~', _CONFIG_FILENAME))

CONFIG_EXAMPLE = """
[DEFAULT]
JIRA_URL = http://webvrt59:8080
JIRA_USER = USER123
JIRA_PASS = Password123
"""

CONFIG_HELP = """

This is config example. Should be in {}.
{}
""".format(CONFIG_FILENAME, CONFIG_EXAMPLE)


def main():
    parser = argparse.ArgumentParser(description=description)

    # group = parser.add_mutually_exclusive_group()
    # group.add_argument("-v", "--verbose", action="store_true")
    # group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s {}'.format(version))

    parser.add_argument('-o', '--outfile', nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout)

    config = configparser.ConfigParser()

    try:
        config.read_file(open(CONFIG_FILENAME))
        jira_url, jira_user, jira_pass = (
            config['DEFAULT']['JIRA_URL'],
            config['DEFAULT']['JIRA_USER'],
            config['DEFAULT']['JIRA_PASS']
        )
    except FileNotFoundError as e:
        message = "Config file {} not found.".format(e.filename)
        parser.error(message + CONFIG_HELP)
    except KeyError as e:
        message = "Config file does not have {} key.".format(e.args[0])
        parser.error(message + CONFIG_HELP)
    except Exception as e:
        message = "Could not read config file at {}".format(CONFIG_FILENAME)
        parser.error(message + CONFIG_HELP)

    args = parser.parse_args()

    try:
        jsl = JiraSprintLogger(jira_url, jira_user, jira_pass)
        jsl.run(output=args.outfile)
    except JiraSprintLoggerError as error:
        parser.error(error)
