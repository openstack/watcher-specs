..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================================================
Improving Unit and Integration Testing for Watcher Dashboard
============================================================

https://blueprints.launchpad.net/watcher/+spec/watcher-dashboard-unit-integration-testing

Watcher Dashboard is the Horizon dashboard plugin for Watcher.
It currently has API unit tests and broken integration tests with no CI
coverage. The watcher-dashboard developers have to manually pull and test
every change in a browser before approving it which is time consuming and
error prone. This specification proposes to improve the testing by adding
unit testing for API and dashboard, and end to end integration testing for
Watcher Dashboard workflows.

Problem description
===================

Watcher Dashboard currently has API unit tests. Selenium based end to end
integration tests are broken due to changes in Horizon. There are no unit tests
for dashboard views and forms. There is no CI coverage for integration tests
to run these tests.

Whenever a developer makes a change to the dashboard, the reviewer manually
pulls the changes locally and tests it in a browser. This is time consuming
and error prone. Many times issues are introduced in the code which got
discovered by users in production.

Below are the current test coverage status:

* **API Unit Tests**: Only working test type, located in ``test/api_tests/``
* **Dashboard Unit Tests**: No unit tests for dashboard views and forms.
* **Integration Tests**: Broken tests in ``test/integration_tests/`` - cannot
  verify UI navigation works correctly.

Use Cases
---------

**As a Watcher Dashboard Developer**, I want to write unit and end to end
integration tests alongside my UI features so that I can verify my changes
work correctly and get automated feedback from CI.

**As a Code Reviewer**, I want to rely on automated test results instead of
manually testing every change in a browser so that I can validate code
functionality efficiently and catch regressions early.

Proposed change
===============

Watcher Dashboard will reorganize testing so CI and reviewers get reliable
automation instead of manual browser checks for every change.

The unit tests and functional tests will use mock and fixtures from Horizon
repo(which uses Django's test framework under the hood) and test data
from ``test/test_data/``.

Integration tests will test user UI interaction workflow against a
live openstack deployment deployed via DevStack in OpenDev CI. The test will
run in headless mode doing real api to validate the full UI workflow.

This specification adopts Playwright for integration tests because it provides
built-in browser management, automatic waiting, code generation tools
(``playwright codegen``), semantic locators, and strong debugging support,
which yields simpler setup and more maintainable tests than Selenium for this
plugin.

Following Manila-UI and Horizon layouts, suites will move from
``test/api_tests/`` and ``test/integration_tests/`` into ``test/unit/api/``,
``test/unit/dashboards/``, and ``test/integration/``, reusing
``test/helpers.py`` and ``test/test_data/``. Suites will run with **stestr**
per the OpenStack Python PTI.

Before watcher-dashboard can depend on Playwright as a global dependency,
contributors must add ``playwright`` to ``global-requirements.txt`` and
upper-constraints in the requirements repository.

What remains is to complete those moves, extend ``test/helpers.py`` where
Horizon patterns require it, add dashboard unit tests using fixtures such as
``self.audit_templates``, ``self.goals``, and ``self.strategies`` from
``test/test_data/watcher_data.py``, maintain Playwright integration tests
behind tox, and add Zuul jobs (for example a DevStack-based
``watcher-dashboard-integration-playwright`` job plus unit jobs) that publish
HTML reports.

The tree and tox entrypoints below summarize layout and how suites are
invoked after the work merges.

.. code-block:: text

    watcher-dashboard/
    └── test/
        ├── helpers.py
        ├── __init__.py
        ├── unit/
        │   ├── api/                          # API unit tests
        │   │   ├── __init__.py
        │   │   └── test_watcher.py
        │   └── dashboards/                   # Dashboard unit tests
        │       ├── __init__.py
        │       ├── test_audit_templates.py
        │       └── test_strategies.py
        │
        ├── integration/                    # Playwright integration tests
        │   ├── __init__.py
        │   ├── base.py                   # Base test class with browser setup
        │   ├── test_audit_workflow.py
        │   └── test_action_plan_workflow.py
        └── test_data/
            ├── __init__.py
            ├── utils.py
            ├── exceptions.py
            └── watcher_data.py

.. code-block:: bash

    tox -e unit-api           # API unit tests
    tox -e unit-dashboard     # Dashboard unit tests
    tox -e integration        # Playwright integration tests

Alternatives
------------

* **Using Selenium for integration testing.** The legacy
  integration tests used Selenium, but were broken and difficult to maintain.
  Alternative frameworks were evaluated through POC implementations.

  **Selenium**: Requires separate WebDriver installation and version
  management, needs explicit waits leading to flaky tests, lacks built-in code
  generation, relies on fragile XPath/CSS selectors, and requires additional
  CI dependencies.

  **Playwright**: Automatically manages browser binaries, includes built-in
  auto-wait reducing flakiness, provides ``playwright codegen`` for test
  generation, uses maintainable semantic locators (role, label, text), has
  simpler CI integration, and offers trace viewer for debugging.

  Given watcher-dashboard's need for reliable and maintainable tests,
  Playwright is the better choice. **Rejected in favor of Playwright.**

* **Pytest-based suites matching Horizon or manila-ui.** Those projects use
  Pytest with Selenium for parts of their UI testing; porting
  watcher-dashboard the same way would mirror them but conflicts with the
  OpenStack Python PTI preference for stestr and standard unittest patterns.
  **Rejected.**

Data model impact
-----------------

None.

REST API impact
---------------

None.

Security impact
---------------

None.

Notifications impact
--------------------

None.

Other end user impact
---------------------

None.

Performance Impact
------------------

None for production.

Other deployer impact
---------------------

None.

Developer impact
----------------

* **Positive impacts**: Automated UI testing, less manual browser testing,
  clearer test layout, stronger regression coverage for UI changes.

* **Learning curve**: Contributors learn Playwright for integration tests and
  Horizon/Django unit patterns; docs supply guidelines and examples.

* **Code review expectations**: New UI features ship with integration tests;
  dashboard views and forms gain unit tests; reviewers skip full manual
  browser runs on every change.

* **Testing requirements**: Going forward, new features added to
  watcher-dashboard should include integration tests to validate UI workflows.
  This ensures consistent test coverage and prevents regressions.

Upgrade impact
--------------

None.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

  chandankumar

Other contributors:

Work Items
----------

* Restructure test directory layout following the proposed structure
* Move existing API tests from ``test/api_tests/`` to ``test/unit/api/``
* Move integration tests from ``test/integration_tests/`` to
  ``test/integration/``
* Update ``test/helpers.py`` to extend Horizon's test infrastructure
* Add unit tests for dashboard views and forms
* Implement and maintain Playwright-based integration tests and tox targets
* Add ``playwright`` to global requirements and upper-constraints where needed
  if accepted otherwise keep `playwright` to test-requirements.txt till other
  horizon dashboard plugins start adopting it.
* Add Zuul jobs for new test targets with HTML reporting
* Create contributor testing documentation

Dependencies
============

Existing (from Horizon):

* ``django.test`` - Django's test framework
* ``unittest.mock`` - Python standard library

New:

* **Playwright**: ``playwright`` (must land in global requirements before
  hard dependency in watcher-dashboard)
* **stestr**: ``stestr``
* **ddt**: ``ddt``

Testing
=======

All test types will be validated by successful CI runs.

Documentation Impact
====================

* ``doc/source/contributor/testing.rst`` - Testing guide
* Updates to ``HACKING.rst`` with test conventions

References
==========

* `Code Quality Improvements and Test Infrastructure for Dashboard`_
* `Functional Test Infrastructure for Watcher`_
* `Django testing documentation`_
* `OpenStack Python PTI Testing guide`_
* `Manila-UI Test Patterns`_
* `Horizon Test Patterns`_
* `stestr`_
* `playwright`_
* `selenium`_

.. _Code Quality Improvements and Test Infrastructure for Dashboard: https://opendev.org/openstack/watcher-specs/src/branch/master/specs/2026.1/approved/testing-and-codequality.rst
.. _Functional Test Infrastructure for Watcher: https://opendev.org/openstack/watcher-specs/src/branch/master/specs/2026.1/approved/functional-testing.rst
.. _Django testing documentation: https://docs.djangoproject.com/en/stable/topics/testing/overview/
.. _OpenStack Python PTI Testing guide: https://governance.openstack.org/tc/reference/pti/python.html#python-test-running
.. _Manila-UI Test Patterns: https://opendev.org/openstack/manila-ui/src/branch/master/manila_ui/tests
.. _Horizon Test Patterns: https://opendev.org/openstack/horizon/src/branch/master/openstack_dashboard/test
.. _stestr: https://opendev.org/openstack/stestr
.. _playwright: https://playwright.dev/python/docs/intro
.. _selenium: https://www.selenium.dev/documentation/

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2026.2
     - Introduced - Improve testing for Watcher Dashboard
