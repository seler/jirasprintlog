from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='jirasprintlog',
      version="0.1",
      description="Simple script that lists JIRA issues from specified sprint.",
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
      ],
      keywords='jira changelog',
      url='http://tasbb-em2-01:7990/projects/PYFRAME',
      author='Rafal Selewonko',
      author_email='rafal.selewonko@willistowerswatson.com',
      license='',
      packages=['jirasprintlog'],
      install_requires=[
          'jira', 'jinja2'
      ],
      test_suite='nose.collector',
      tests_require=[],
      entry_points={
          'console_scripts': ['jira-sprint-log=jirasprintlog.commandline:main'],
      },
      include_package_data=True,
      zip_safe=False)
