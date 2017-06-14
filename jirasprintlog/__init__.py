#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import itertools

from jinja2 import Template
from jira import JIRA


"""
Simple script that lists JIRA issues from specified sprint.
"""
__author__ = "Rafal Selewonko <rafal@selewonko.com>"

# https://www.python.org/dev/peps/pep-0008/#version-bookkeeping
# https://www.python.org/dev/peps/pep-0440/
__version_info__ = (0, 1, 'dev1',)
__version__ = '.'.join(map(str, __version_info__))


OUTPUT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>JIRA report</title>
    <meta charset="utf-8" />
</head>
<body>
    <h2>
        {% for sprint in sprints %}
            {{ sprint }}
            {% if not loop.last %}, {% endif %}
        {% endfor %}
    </h2>
    <ul>
    {% for issue in issues %}
      <li>
        <a href="{{ issue.permalink() }}">
          {{ issue.key }}
        </a> - {{ issue.fields.summary }}
      </li>
    {% endfor %}
    </ul>
</body>
</html>
"""


class JiraSprintLoggerError(Exception):
    pass


class JiraSprintLogger(object):

    def __init__(self, jira_url, jira_user, jira_pass,
                 stdin=sys.stdin, stdout=sys.stdout):
        self.stdin = stdin
        self.stdout = stdout
        self.jira = JIRA({'server': jira_url}, basic_auth=(jira_user, jira_pass))

    def run(self, output):
        board = self.get_board()
        sprints = tuple(self.get_sprints(board))

        issues = self.get_issues(sprints)
        self.render(output, sprints, issues)

    @staticmethod
    def render(output, sprints, issues):
        template = Template(OUTPUT_TEMPLATE)
        result = template.stream(sprints=sprints, issues=issues)
        result.dump(output)

    @staticmethod
    def __retrieve(call, startAt, maxResults, args, kwargs):
        return iter(call(*args, startAt=startAt, maxResults=maxResults, **kwargs))

    def _retrieve(self, call, *args, startAt=0, maxResults=50, **kwargs):
        i = 0
        results = self.__retrieve(call, startAt, maxResults, args, kwargs)

        # do not fear this line, iterators raise StopIteration
        while True:
            try:
                yield next(results)
                i += 1
            except StopIteration as error:
                if i < maxResults:
                    raise error
                else:
                    i = 0
                    startAt += maxResults
                    results = self.__retrieve(call, startAt, maxResults, args, kwargs)

    def _display_select_options(self, iterable, name):
        self.stdout.write("Available {}s:\n".format(name))
        for i, item in enumerate(iterable):
            self.stdout.write("{}: {}\n".format(i + 1, item))

        self.stdout.write("Choose {} (insert number and hit return):\n".format(name))

    def _select(self, iterable, name):
        iterable = tuple(iterable)
        self._display_select_options(iterable, name)
        line = self.stdin.readline()
        try:
            return iterable[int(line) - 1]
        except (IndexError, ValueError):
            raise JiraSprintLoggerError("Invalid {}.".format(name))

    def _select_multiple(self, iterable, name):
        iterable = tuple(iterable)
        self._display_select_options(iterable, name)
        line = self.stdin.readline()
        for line in line.split(','):
            try:
                yield iterable[int(line) - 1]
            except (IndexError, ValueError):
                raise JiraSprintLoggerError("Invalid {}.".format(name))

    def get_board(self):
        boards = self._retrieve(self.jira.boards)
        return self._select(boards, 'board')

    def get_sprints(self, board):
        sprints = tuple(self._retrieve(self.jira.sprints, board_id=board.id))
        return self._select_multiple(sprints, 'sprint')

    def _get_issues(self, sprint):
        pattern = 'sprint={} and status=DONE'.format(sprint.id)
        return self._retrieve(self.jira.search_issues, pattern, fields='summary')

    def get_issues(self, sprints):
        return itertools.chain.from_iterable(self._get_issues(sprint) for sprint in sprints)
