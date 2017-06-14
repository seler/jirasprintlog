import io
from unittest import TestCase, mock, main
from jinja2 import Template

from jirasprintlog import JiraSprintLogger, OUTPUT_TEMPLATE, JiraSprintLoggerError


class JiraSprintLoggerTestCase(TestCase):
    jira_url = 'http://example.com'
    jira_user = 'root'
    jira_pass = 'root'

    @mock.patch('jirasprintlog.JIRA')
    def setUp(self, JIRA):
        self.JIRA = JIRA
        self.jsl = JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass)

    def _get_issues(self, n=10):
        issues = []
        for i in range(n):
            issue = mock.MagicMock(key='ASD-123{}'.format(i))
            issue.permalink.return_value = 'ASD-123{}-permalink'.format(i)
            issue.fields = mock.MagicMock(summary='ASD-123{}-summary'.format(i))
            issues.append(issue)
        return issues

    @mock.patch('jirasprintlog.JIRA')
    def test_init_authorizes_jira(self, JIRA):
        JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass)
        JIRA.assert_called_with(
            {'server': self.jira_url},
            basic_auth=(self.jira_user, self.jira_pass))

    def test_run_gets_board_sprint_issues_and_runs_render(self):
        board = mock.MagicMock()
        self.jsl.get_board = mock.MagicMock(return_value=board)

        sprint = mock.MagicMock()
        sprint.__str__.return_value = "Sprint Name"
        sprints = (sprint, )
        self.jsl.get_sprints = mock.MagicMock(return_value=sprints)

        issues = mock.MagicMock()
        self.jsl.get_issues = mock.MagicMock(return_value=issues)

        self.jsl.render = mock.MagicMock()

        outfile = io.StringIO()
        self.jsl.run(outfile)

        self.jsl.get_board.assert_called_once_with()
        self.jsl.get_sprints.assert_called_once_with(board)
        self.jsl.get_issues.assert_called_once_with(sprints)
        self.jsl.render.assert_called_once_with(outfile, sprints, issues)

    def test_render_writes_template(self):
        issues = self._get_issues(5)
        sprint = mock.MagicMock()
        sprint.__str__.return_value = "Sprint Name"
        outfile = io.StringIO()
        self.jsl.render(outfile, [sprint], issues)
        outfile.seek(0)
        actual = outfile.read()
        expected = Template(OUTPUT_TEMPLATE).render(sprints=[sprint], issues=issues)
        self.assertEqual(expected, actual)

    def test_retrieve_helper(self):
        issues = self._get_issues(10)
        call = mock.MagicMock(return_value=issues)
        startAt = 0
        maxResults = 10
        args = (1, 2, 3)
        kwargs = {'a': 1, 'b': 2, 'c': 3}
        result = self.jsl._JiraSprintLogger__retrieve(
            call, startAt, maxResults, args, kwargs)
        call.assert_called_once_with(
            *args, startAt=startAt, maxResults=maxResults, **kwargs)
        self.assertEqual(tuple(issues), tuple(result))

    def test_retrieve(self):
        expected = tuple(range(9))
        call = mock.MagicMock(return_value=expected)
        args = (1, 2, 3)
        kwargs = {'a': 1, 'b': 2, 'c': 3}
        actual = tuple(self.jsl._retrieve(
            call, *args, startAt=0, maxResults=1000, **kwargs))
        call.assert_called_once_with(*args, startAt=0, maxResults=1000, **kwargs)
        self.assertEqual(expected, actual)

    def test_retrieve_paginates(self):
        expected = tuple(range(101))

        def call(startAt=0, maxResults=50):
            return expected[startAt:startAt + maxResults]

        actual = tuple(self.jsl._retrieve(call, maxResults=10))

        self.assertEqual(expected, actual)

    def test_get_board_gets_board(self):
        boards = [
            mock.MagicMock(id=1),
            mock.MagicMock(id=2),
            mock.MagicMock(id=3)
        ]
        expected = boards[0]
        self.JIRA.return_value.boards.return_value = boards
        self.jsl._select = mock.MagicMock(return_value=expected)

        actual = self.jsl.get_board()

        self.assertEqual(expected, actual)

    def test_get_sprints_gets_sprints(self):
        sprints = (
            mock.MagicMock(id=1),
            mock.MagicMock(id=2),
            mock.MagicMock(id=3)
        )
        expected = sprints[:1]
        self.JIRA.return_value.sprints.return_value = sprints
        self.jsl._select_multiple = mock.MagicMock(return_value=expected)
        board = mock.MagicMock(id=1)

        actual = self.jsl.get_sprints(board)

        self.assertEqual(expected, tuple(actual))

    def test_get_issues_gets_issues(self):
        expected = [
            mock.MagicMock(id=1),
            mock.MagicMock(id=2),
            mock.MagicMock(id=3)
        ]
        sprints = (mock.MagicMock(id=1), )
        self.JIRA.return_value.search_issues.return_value = expected

        actual = list(self.jsl.get_issues(sprints))

        self.assertEqual(expected, actual)

    @mock.patch('jirasprintlog.JIRA')
    def test_select_writes_options(self, JIRA):
        stdin = io.StringIO('1\n')
        stdout = io.StringIO()
        jsl = JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass,
                               stdin=stdin, stdout=stdout)
        options = [
            'lorem',
            'ipsum',
            'dolor'
        ]
        jsl._select(options, 'text')
        stdout.seek(0)
        printed = stdout.read()
        self.assertIn('1: lorem', printed)
        self.assertIn('2: ipsum', printed)
        self.assertIn('3: dolor', printed)

    @mock.patch('jirasprintlog.JIRA')
    def test_select_selects(self, JIRA):
        stdin = io.StringIO('1\n')
        stdout = io.StringIO()
        jsl = JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass,
                               stdin=stdin, stdout=stdout)
        options = [
            'lorem',
            'ipsum',
            'dolor'
        ]
        selected = jsl._select(options, 'text')
        self.assertEqual(selected, options[0])

    @mock.patch('jirasprintlog.JIRA')
    def test_select_invalid_option_int(self, JIRA):
        stdin = io.StringIO('4\n')
        stdout = io.StringIO()
        jsl = JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass,
                               stdin=stdin, stdout=stdout)
        options = [
            'lorem',
            'ipsum',
            'dolor'
        ]
        self.assertRaises(JiraSprintLoggerError, jsl._select, options, 'text')

    @mock.patch('jirasprintlog.JIRA')
    def test_select_invalid_option_string(self, JIRA):
        stdin = io.StringIO('asdf\n')
        stdout = io.StringIO()
        jsl = JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass,
                               stdin=stdin, stdout=stdout)
        options = [
            'lorem',
            'ipsum',
            'dolor'
        ]
        self.assertRaises(JiraSprintLoggerError, jsl._select, options, 'text')


if __name__ == '__main__':
    main()
