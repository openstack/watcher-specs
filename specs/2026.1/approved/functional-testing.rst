..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Functional Test Infrastructure for Watcher
==========================================

https://blueprints.launchpad.net/watcher/+spec/functional-test-infrastructure

Introduce functional testing infrastructure to Watcher, enabling testing of
multi-component workflows with minimal mocking. This improves test coverage
for complex service interactions (API, decision engine, applier) and provides
regression protection for bugs requiring integration testing to reproduce.

Problem description
===================

Watcher currently has excellent unit test coverage but lacks functional tests
that verify multiple components working together. This gap makes it difficult
to:

* Catch integration bugs that unit tests miss due to extensive mocking
* Test real workflows (audit → strategy → action plan → applier)
* Validate RPC interactions between services with real message passing
* Reproduce complex bugs that require service interaction
* Test API behavior with real WSGI application
* Verify notification emission in realistic scenarios

Unit tests with heavy mocking can give false confidence - tests pass but the
integrated system fails in production. Functional tests fill this gap by
testing real code paths with minimal mocking.

Use Cases
---------

**As a Watcher Developer**, I want to write functional tests so that I can
verify my changes work correctly when multiple components interact, without
needing a full OpenStack deployment.

**As a Watcher Core Reviewer**, I want functional tests for complex bug fixes
so that I can be confident the bug is truly fixed and won't regress.

**As a Watcher Operator**, I benefit from functional tests catching integration
bugs before release, resulting in more stable deployments.

**As a Watcher Contributor**, I want clear examples and documentation for
functional testing so I can add tests for my features without deep knowledge
of the test infrastructure.


Proposed change
===============

Implement functional testing infrastructure adapted from OpenStack patterns
(Nova, Placement) for Watcher's architecture (Pecan API, decision engine,
applier services).

The infrastructure provides:

* Reorganized test structure: ``watcher/tests/unit/`` and
  ``watcher/tests/functional/``
* Reusable fixtures for database, RPC, external services, API server
* ``WatcherFunctionalTestCase`` base class with automatic fixture setup
* Gabbi (YAML) tests for declarative API contract testing
* Regression test framework with documentation
* Contributor guide for functional testing

The implementation follows "minimize mocks, maximize reality" - functional
tests use real Watcher code (API, database, RPC) and only mock external
services (Nova, Gnocchi).

**Key Design:**

* SQLite in-memory with schema caching for speed
* oslo.messaging fake driver for deterministic RPC
* wsgi-intercept for in-process HTTP (no network I/O)
* Python and Gabbi (YAML) test formats
* Reuse existing helpers (``watcher/tests/db/utils.py``)

**Directory Structure:**

.. code-block:: text

    watcher/tests/
    ├── unit/                      # All existing tests (moved)
    │   ├── api/
    │   ├── decision_engine/
    │   ├── applier/
    │   └── ...
    ├── functional/                # New functional tests
    │   ├── base.py               # WatcherFunctionalTestCase
    │   ├── test_api_audits.py    # Python functional tests
    │   ├── test_workflows.py     # End-to-end workflow tests
    │   ├── test_api_gabbi.py     # Gabbi test loader
    │   ├── fixtures/             # Gabbi-specific fixtures
    │   │   ├── gabbi.py
    │   │   └── capture.py
    │   ├── gabbits/              # Gabbi YAML tests
    │   │   ├── audit-lifecycle.yaml
    │   │   ├── microversions.yaml
    │   │   └── ...
    │   └── regressions/          # Bug-specific tests
    │       └── test_bug_*.py
    ├── local_fixtures/            # Shared fixtures
    │   ├── conf.py               # Configuration fixture
    │   ├── database.py           # Database fixture
    │   ├── rpc.py                # RPC fixtures
    │   ├── notifications.py      # Notification capture
    │   ├── api.py                # API server fixture
    │   ├── service.py            # Service fixture
    │   ├── nova.py               # Nova mock
    │   └── gnocchi.py            # Gnocchi mock
    ├── fixtures/                  # Existing test fixtures
    │   └── watcher.py
    └── helpers.py                 # Test helper functions

**Test Execution:**

.. code-block:: bash

    tox -e py3                    # Unit tests
    tox -e functional             # All functional tests
    tox -e functional-regression  # Regression tests only

Alternatives
------------

**Full Integration Tests Only:** Deploy real external services via DevStack.
Rejected - too slow (30+ min), complex setup, network flakiness.

**Unit Tests Only:** Rely on existing unit tests and Tempest. Rejected -
misses integration bugs, complex scenarios hard to reproduce.

**Docker Containers:** Run services in containers. Rejected - adds complexity,
slower, doesn't align with OpenStack patterns.

**Tempest Only:** Use only Tempest for integration. Rejected - too slow for
regular development, doesn't replace functional tests.

Data model impact
-----------------

None. Functional tests use the existing data model. The database fixture
applies existing migrations to create the schema.

REST API impact
---------------

None. Functional tests validate existing API behavior. The Gabbi test
infrastructure will improve API testing coverage and make microversion
testing easier, but does not change the API itself.

Security impact
---------------

None.

Notifications impact
--------------------

None. Functional tests validate existing notification behavior. The
notification fixture captures emitted notifications for verification but
does not change notification emission logic.

Other end user impact
---------------------

None.

Performance Impact
------------------

None

Other deployer impact
---------------------

None.

Developer impact
----------------

Positive impacts: easier end to end tests, better regression protection,
clearer test organization, lower barrier for API testing.

Learning curve: developers learn when to use functional vs unit tests,
documentation provides guidelines and examples.

Code review expectations: functional tests for complex bug fixes, multi-
component workflows, API changes (Gabbi tests), and RPC features.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

  sean-k-mooney

Other contributors:

  None

Work Items
----------

* Extract existing fixtures and create test helpers
* Reorganize tests: move to ``unit/``, create ``functional/``
* Core fixtures: database, RPC, notifications, config
* Service fixtures: Nova, Gnocchi mocks
* API fixture: Pecan with wsgi-intercept
* Service fixture: decision engine, applier
* Base test class: ``WatcherFunctionalTestCase``
* Gabbi infrastructure: loader, fixtures, YAML examples
* Example tests: API tests, workflow tests
* Regression framework: directory structure, guidelines, README
* Documentation: contributor guide for functional/Gabbi tests
* CI integration: tox.ini, .zuul.yaml, stestr config

See detailed implementation plan: https://gist.github.com/SeanMooney/43afa55282d2286a312eae7f3c7709e2

Dependencies
============

No new runtime dependencies.

test dependencies will be extended using existing libraries:
used in nova and placement.

* gabbi - YAML HTTP testing (in requirements)
* wsgi-intercept - In-process HTTP (in requirements)
* oslo.messaging - RPC with fake driver (in use)
* oslo.db - Database fixtures (in use)
* oslo.config - Configuration management (in use)
* oslo.log - Logging (in use)
* oslo.policy - Policy enforcement (in use)

Testing
=======

Validation approach: each phase validated before proceeding. Unit test suite
validates reorganization, fixture tests validate cleanup/behavior
a zuul job will be added to run the functional tests once a minium test case is
written and will self validate the functional tests as they are expanded.


Documentation Impact
====================

New documentation:

* Contributor guide for functional testing
  (``doc/source/contributor/functional-testing.rst``): covers functional vs
  unit tests, Python and Gabbi test writing, fixture usage, running/debugging,
  best practices
* Regression testing guide
  (``watcher/tests/functional/regressions/README.rst``): when to write
  regression tests, naming conventions, structure requirements
* API documentation: Gabbi tests serve as executable examples

Updated documentation:

* Testing guidelines: add functional vs unit test section
* README.rst: update with functional test commands

References
==========

**Implementation Details:**

* Detailed implementation plan: https://gist.github.com/SeanMooney/43afa55282d2286a312eae7f3c7709e2
* How Nova functional tests work: https://gist.github.com/SeanMooney/0bc41721481dd6e5918a4504c956f882
* How Gabbi tests work in Placement: https://gist.github.com/SeanMooney/36f2ef20bd5cb4c853af23c581b917fc

**OpenStack References:**

* `Nova Functional Tests <https://docs.openstack.org/nova/latest/contributor/testing/functional-tests.html>`_
* `Placement Gabbi Tests <https://opendev.org/openstack/placement/src/branch/master/placement/tests/functional/gabbits>`_
* `Gabbi Documentation <https://gabbi.readthedocs.io/>`_

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2026.1
     - Introduced

