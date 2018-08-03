Developer's guide
=================

This section contains information on how to perform various task and an overview
of how our development infrastructure is set up.

Local development
-----------------

These tasks are usually performed on an individual developer's machine.

Make database migrations
````````````````````````

The ``makemigrations`` command cannot be run directly since the application
directory is mounted read-only within the container. The work around is a little
ugly at the moment:

1. In ``compose/development.yml``, comment out the ``read_only: true`` value
   from the volume defined in ``development_app``.
2. Run ``./compose.sh development run --rm development_app ./manage.py makemigrations ...``
   as usual.
3. Uncomment the ``read_only: true`` commented out in 1.
4. Change permissions on the migration: ``sudo chmod $USER path/to/migration.py``

.. _run-tests:

Run the test suite
``````````````````

The `tox <https://tox.readthedocs.io/>`_ automation tool is used to run tests
inside their own virtualenv. This way we can be sure that we know which packages
are required to run the tests. By default tests are run in a Postgres database
created by docker-compose. Other databases can be used by setting the
``DJANGO_DB_...`` environment variables. See :any:`database-config`.

.. code-block:: bash

    $ ./tox.sh

By default, ``tox`` will run the test suite using the version of Python used
when we deploy and will compile a local version of the documentation. The ``-e``
flag may be used to explicitly specify an environment to run. For example, to
build only the documentation:

.. code-block:: bash

    $ ./tox.sh -e doc

Tox runs tests within persistent virtualenvs. Tox attempts to determine when it
should rebuild the virtualenv but its logic can sometimes be imperfect. This is
especially true in the case of dependencies hidden deep in the various
``requirements/{...}.txt`` files. Should it appear that a module is not
installed when it should be, the ``-r`` flag can be passed to tox:

.. code-block:: bash

    $ ./tox.sh -r          # recreate all environments
    $ ./tox.se -e py36 -r  # recreate only the py36 environment

.. _toxenvs:

tox environments
````````````````

The following tox environments are available.

py3
    Run by default. Launch the test suite under Python 3. Generate a
    code-coverage report and display a summary coverage report.

doc
    Run by default. Build documentation and write it to the ``build/doc/``
    directory.

flake8
    Run by default. Check for code-style violations using the `flake8
    <http://flake8.pycqa.org/>`_ linter.

manage
    Run management commands. Positional arguments are passed to ``manage.py``.

.. _devserver:

Run the development server
``````````````````````````

Django comes with a development web server which can be run via:

.. code-block:: bash

    $ ./compose.sh development

The server should now be browsable at http://localhost:8080/.

Building the documentation
``````````````````````````

This documentation may be built using the "doc" :any:`tox environment
<toxenvs>`.

Docker images
-------------

The application is deployed using `Docker
<https://docker.com/>`_ containers on the Google Container Engine. Similarly,
docker-compose can be used to run the application locally in a Docker container.

.. note::

    If the ``requirements.txt`` file is modified, you'll need to re-build the
    container image via ``docker-compose build``.

Occasionally, it is useful to get an interactive Python shell which is set up to
be able to import the application code and to make database queries, etc. You
can launch such a shell via:

.. code-block:: bash

    $ ./compose.sh development up -d  # if the server is not yet running
    $ ./compose.sh development run --rm development_app ./manage.py shell

Running the production docker image
```````````````````````````````````

The production Docker image is built with the top-level Dockerfile. To test it,
you can build and run the production image via:

.. code-block:: bash

    $ ./compose.sh development down  # if already started
    $ ./compose.sh production build
    $ ./compose.sh production up -d  # start server in background
    $ ./compose.sh production exec production_app ./manage.py migrate

.. note::

    The production docker-compose configuration **does not** mount the working
    directory inside the container so you have to make sure that you re-build
    the image.

Cloud infrastructure
--------------------

This section provides a brief outline of cloud infrastructure for development.

Source control
``````````````

The panel is hosted on GitHub at https://github.com/uisautomation/sms-webapp.
The repository has ``master`` set up to be writeable only via pull request. It
is intended that local development happens in personal forks and is merged via
pull request. The main rationale for this is a) it guards against accidentally
``git push``-ing the wrong branch and b) it reduces the number of "dangling"
branches in the main repository.

.. _travisci:

Unit tests
``````````

The project is set up on `Travis CI <https://travis-ci.org/>`_ to automatically
run unit tests and build documentation on each commit to a branch and on each
pull request.

.. note::

    By logging into Travis CI via GitHub, you can enable Travis CI for your
    personal fork. This is **highly recommended** as you'll get rapid feedback
    via email if you push a commit to a branch which does not pass the test
    suite.

In order to better match production, Travis CI is set up to run unit tests using
the PostgreSQL database and *not* sqlite. If you only run unit tests locally
with sqlite then it is possible that some tests may fail.

Code-coverage
`````````````

Going to `CodeCov <https://codecov.io/>`_, logging in with GitHub and adding the
``sms-webapp`` repository will start code coverage reporting on pull-requests.

Documentation
`````````````

Travis CI has been set up so that when the master branch is built, the
documentation is deployed to https://uisautomation.github.io/sms-webapp via
GitHub pages. The `UIS robot <https://github.com/bb9e/>`_ machine account's
personal token is set up in Travis via the ``GITHUB_TOKEN`` environment
variable.

.. seealso::

    Travis CI's `documentation
    <https://docs.travis-ci.com/user/deployment/pages/>`_ on deploying to GitHub
    pages.

Code-style
``````````

The ``tox`` test runner will automatically check the code with `flake8
<http://flake8.pycqa.org/>`_ to ensure PEP8 compliance. Sometimes, however,
rules are made to be broken and so you may find yourself needing to use the
`noqa in-line comment
<http://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors>`_
mechanism to silence individual errors.

To run the flake8 tests manually, specify the tox environment:

.. code:: bash

    $ ./compose.sh tox run --rm tox -e flake8

Documentation
`````````````

This documentation is re-built on each commit to master by Travis and posted to
GitHub pages at https://uisautomation.github.io/sms-webapp/.
