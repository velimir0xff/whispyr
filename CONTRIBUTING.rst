.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/velimir0xff/whispyr/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

whispyr could always use more documentation, whether as part of the
official whispyr docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/velimir0xff/whispyr/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up ``whispyr`` for local development.

1. Fork the ``whispyr`` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/whispyr.git

3. Install your local copy into a virtualenv. Assuming you have ``pipenv`` installed, this is how you set up your fork for local development. Run from directory where your fork is cloned to (``whispyr`` by default)::

    $ pipenv install --dev
    $ pipenv shell

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 whispyr tests
    $ py.test

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7, 3.4, 3.5, 3.6 and 3.7. Check
   https://travis-ci.org/velimir0xff/whispyr/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

  $ py.test ./tests/test_whispyr_templates.py

Or you can even limit tests to a single test case using a matching expression for ``-k`` parameter::

  $ py.test ./tests/test_whispyr_client_basic.py -k test_do_not_retry_qpd


Record VCRs
-----------

Whenever you need a new ``Whispir`` collection (such as ``workspaces``) ``whispyr`` test should be updated accordingly. Collections tests utilises ``vcrpy`` library.
To run tests in recording mode with new (or changed) collections tests should be supplied with all required credentials to be able to talk to whispir.io. You can see them all in a help section of ``py.test``. They starts with a ``--whispir`` prefix::

  custom options:
  --whispir-username=WHISPIR_USERNAME
                        Whispir username
  --whispir-password=WHISPIR_PASSWORD
                        Whispir password
  --whispir-api-key=WHISPIR_API_KEY
                        Whispir API key
  --whispir-gcm-api-key=WHISPIR_GCM_API_KEY
                        Whispir Google Cloud Messaging API key

And then configure ``py.test`` to use credentials to record cassettes::

  $ py.test ./tests/test_whispyr_devices.py \
      --whispir-username WHISPIR_USERNAME   \
      --whispir-password WHISPIR_PASSWORD   \
      --whispir-api-key WHISPIR_API_KEY     \
      --whispir-gcm-api-key WHISPIR_GCM_API_KEY

Once new cassette is recorded please make sure you don't have any sensitive information in them.
To automated this process you can install https://github.com/awslabs/git-secrets and add the following patterns into your exclusion list::

  $ git secrets --add 'apikey=[^&]*'
  $ git secrets --add --allowed apikey=V4L1D4P1K3Y
  $ git secrets --add --allowed apikey=TEST_API_KEY
  $ git secrets --add 'Basic\s+[a-zA-Z0-9=]+'
  $ git secrets --add --allowed 'Basic VTUzUk40TTM6UDRaWlcwUkQ='
  $ git secrets --add '"gcmApiKey":\s*"[^"]*"'
  $ git secrets --add --allowed '"gcmApiKey": "9OO9l3ClouDm355491n94P1K3y"'


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

  $ bumpversion patch # possible: major / minor / patch
  $ git push
  $ git push --tags

Travis will then deploy to PyPI if tests pass.
