import io
from unittest import mock, TestCase, main
from jinja2 import Template

from jirasprintlog import JiraSprintLogger, OUTPUT_TEMPLATE


class JiraSprintLoggerTestCase(TestCase):
    jira_url = 'http://example.com'
    jira_user = 'root'
    jira_pass = 'root'

    @mock.patch('jirasprintlog.JIRA')
    def test_tool_renders_results(self, JIRA):


        stdin = io.StringIO('1\n1\n')
        stdout = io.StringIO()
        outfile = io.StringIO()
        jsl = JiraSprintLogger(self.jira_url, self.jira_user, self.jira_pass,
                               stdin=stdin, stdout=stdout)
        JIRA.assert_called_with(
            {'server': self.jira_url},
            basic_auth=(self.jira_user, self.jira_pass))


        JIRA.return_value.boards.return_value = [
            mock.MagicMock(id=1),
            mock.MagicMock(id=2),
            mock.MagicMock(id=3)
        ]

        sprint = mock.MagicMock()
        sprint.__str__.return_value = "Sprint Name"

        JIRA.return_value.sprints.return_value = [
            sprint,
            mock.MagicMock(id=2),
            mock.MagicMock(id=3)
        ]

        issues = []
        for i in range(10):
            issue = mock.MagicMock(key='ASD-123{}'.format(i))
            issue.permalink.return_value = 'ASD-123{}-permalink'.format(i)
            issue.fields = mock.MagicMock(summary='ASD-123{}-summary'.format(i))
            issues.append(issue)

        JIRA.return_value.search_issues.return_value = issues

        jsl.run(outfile)

        outfile.seek(0)
        actual = outfile.read()

        self.assertIn(str(sprint), actual)

        expected = Template(OUTPUT_TEMPLATE).render(sprints=(sprint, ), issues=issues)
        self.maxDiff = None
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    main()
