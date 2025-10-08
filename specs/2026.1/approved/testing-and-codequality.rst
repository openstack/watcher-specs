..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===============================================================
Code Quality Improvements and Test Infrastructure for Dashboard
===============================================================

https://blueprints.launchpad.net/watcher/+spec/dashboard-code-quality-testing

Improve code quality and test infrastructure for Watcher Dashboard by
eliminating patterns that hinder static analysis, adopting centralized
configuration management, and restructuring tests to support reusable fixtures
following the pattern established in the main Watcher project.

This work addresses technical debt in the Watcher Dashboard codebase that
impedes maintainability and developer productivity. The changes will improve
IDE support, enable better static analysis, and create a more maintainable
codebase for future development.

Problem description
===================

Watcher Dashboard currently uses code patterns that create robustness issues
and reduce code quality:

* Direct symbol imports (``from X import Y``) create fragile dependencies
  that can break during refactoring and make it difficult to understand
  module relationships
* Reflection helpers (``getattr/hasattr/setattr``) used for static attributes
  hide potential AttributeError bugs and make code behavior unpredictable
* Django settings accessed directly via ``getattr()`` throughout codebase with
  scattered defaults and no validation, creating silent failures and
  configuration drift
* Test infrastructure lacks reusable fixture pattern, leading to inconsistent
  test setup and potential test pollution
* No test structure to accommodate future functional testing with playwright
* Inconsistent code patterns make the codebase harder to review and maintain

These patterns reduce code robustness by hiding errors, creating fragile
dependencies, and making the codebase harder to understand and maintain.

Use Cases
---------

* As a Watcher Dashboard Developer, I would like to refactor code with
  confidence that errors will be caught early rather than hidden by reflection
  helpers, so that I can make changes safely without introducing subtle bugs.

* As a Watcher Core Reviewer, I would like to review code changes efficiently
  without getting distracted by inconsistent patterns or debugging test issues,
  so that I can focus on the actual functionality being implemented.

* As a New Contributor, I would like to understand the codebase quickly and
  write code that follows established patterns, so that I can contribute
  effectively without extensive mentoring on style and structure.


Proposed change
===============

Eliminate code patterns that hinder static analysis and modernize the test
infrastructure to align with established OpenStack practices. The changes
will improve IDE support, enable better static analysis, and create a more
maintainable codebase.

The primary focus is converting direct symbol imports to module-level imports
throughout the codebase, replacing static reflection helpers with direct
attribute access, and centralizing Django settings access through a typed
configuration module. Test infrastructure will be restructured to support
reusable fixtures following the pattern used in the main Watcher project,
with tests organized in ``watcher_dashboard/test/unit/`` and new
``local_fixtures/`` and ``playwright/`` directories for future testing
needs.

A centralized configuration module (``watcher_dashboard/config.py``) will
provide typed, validated access to Django settings, eliminating scattered
``getattr(settings, ...)`` usage throughout the codebase. This module will
be inspired by manila-ui's features.py pattern but enhanced with type hints
and comprehensive validation. CI enforcement will be added to prevent
regression of these patterns, and comprehensive contributor documentation
will be created to guide future development practices.


Alternatives
------------

**Status Quo:** Continue with current patterns. Rejected - technical debt
accumulates as new code follow existing anti-patterns.


**Skip Test Restructure:** Keep flat test structure. Rejected - misses
opportunity to align with main Watcher project patterns and prepare for future
functional testing with playwright.

Data model impact
-----------------

None.

REST API impact
---------------

None.

Security impact
---------------

Positive impact: centralized configuration with validation reduces risk of
misconfiguration. Explicit imports improve code audibility. No new security
concerns introduced.

Notifications impact
--------------------

None.

Other end user impact
---------------------

None. These are internal improvements transparent to dashboard users.

Performance Impact
------------------

Negligible positive impact: ``@memoized.memoized`` decorator on config
functions provides efficient caching of settings lookups. Module-level imports
resolve once rather than on each use.

Other deployer impact
---------------------

None.

Developer impact
----------------

Significant positive impacts:

* **Improved IDE support**: Module-level imports enable accurate autocomplete,
  go-to-definition, and refactoring across all modern Python IDEs
* **Static analysis**: Type-hinted config module and reduced reflection enable
  mypy checking and catch bugs before runtime
* **Easier testing**: Fixture pattern reduces boilerplate; config module
  functions are easier to mock than settings access
* **Better documentation**: Centralized config module serves as living
  documentation of available settings with docstrings

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

* Refactor import patterns to use module-level imports throughout the codebase
* Replace static reflection helpers with direct attribute access
* Create centralized configuration module for Django settings access
* Restructure test directory to support reusable fixtures and future testing
* Add CI enforcement for import and reflection policies
* Create comprehensive contributor documentation for code quality standards
* Implement optional type hints with mypy configuration

See detailed implementation plan:
https://gist.github.com/SeanMooney/f56c7fd6f55ac48958a5c549e1701b6c

Dependencies
============

No new runtime dependencies.

Test dependencies extended using existing libraries proven in OpenStack:

* ``fixtures>=3.0.0`` - Reusable test fixture pattern (already in use in Nova,
  Placement, and main Watcher project)

All other dependencies already in use:

* ``horizon.utils.memoized`` - Configuration caching (in use)
* ``django.conf.settings`` - Django settings (in use)
* ``unittest.mock`` - Test mocking (in use)

Testing
=======

The centralized configuration module will require comprehensive unit test
coverage to ensure proper validation and error handling. Documentation will
be validated through Sphinx builds and RST syntax checking.

The refactoring of the test structure will enable functional testing with
playwright to be added which will eventually be tested with a new zuul job.
that is out of scope for this spec.

Documentation Impact
====================

Comprehensive contributor documentation will be created to establish and
maintain the new code quality standards. Two new documentation files will
be added: ``doc/source/contributor/code_quality.rst`` containing policies
and standards for import patterns, configuration access, reflection usage,
and testing practices, and ``doc/source/contributor/code_patterns.rst``
providing concrete examples and common anti-patterns to avoid.


References
==========

* Detailed implementation plan:
  https://gist.github.com/SeanMooney/f56c7fd6f55ac48958a5c549e1701b6c

* Functional Test Infrastructure blueprint:
  https://blueprints.launchpad.net/watcher/+spec/functional-test-infrastructure

* `Manila-UI features.py
  <https://opendev.org/openstack/manila-ui/src/branch/master/manila_ui/features.py>`_
  - Config module pattern inspiration

* `Python fixtures library <https://pypi.org/project/fixtures/>`_ - Test
  fixture pattern used across OpenStack

* `OpenStack Testing Standards
  <https://docs.openstack.org/hacking/latest/user/hacking.html>`_ - Import
  ordering and style

* `PEP 484 <https://peps.python.org/pep-0484/>`_ - Type Hints

* `PEP 585 <https://peps.python.org/pep-0585/>`_ - Type Hinting Generics (3.10+
  syntax)

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2026.1
     - Introduced
