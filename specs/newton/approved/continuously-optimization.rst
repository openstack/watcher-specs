=============================================
Watcher Continuous Optimization
=============================================

https://blueprints.launchpad.net/watcher/+spec/continuously-optimization


Problem description
===================

`Cluster`_ can be optimized by different `Strategies`_ only when they have
been triggered by `Administrator`_. Launching a recommended `Action Plan`_
manually is not always suitable since state of cluster is constantly changing.
It would be better to have two ways of launching audit: either by triggering
it manually or by launching it periodically.
We propose to include continuous optimization as continuous type of
audit object in Watcher Project.

The main purpose of this change is to design and implement active mode of
Watcher's audit.

This specification relates to blueprint:
https://blueprints.launchpad.net/watcher/+spec/continuously-optimization

Use Cases
---------

As the Administrator I want to create `Audit`_ with CONTINUOUS type.
I specify periodic time with --period parameter (in seconds) to run audit
every 600 seconds. Running audit will create action plan every 600 seconds.

Project Priority
----------------

Not relevant because Watcher is not in the big tent so far.


Proposed change
===============

To perform audits with continuous type we can use periodic_task decorator
from oslo_service module on 'launch_audits_periodically' method. This method
gets continuous type audits with (PENDING, ONGOING) states. If some
of them are not in audits_to_launch list we add them to that list and to the
ThreadPoolExecutor. Once audit is added to thread, this thread is going to
sleep for PERIOD seconds. After this audit will be executed and UUID of audit
will be removed from audits_to_launch list.
To keep track of the triggered audit, notification has to be pushed on
the message bus every time the audit is re-triggered.
When a new action plan is proposed, Watcher should cancel all the previously
generated action plans (and actions) with same Audit Template become obsolete
and therefore their state should be changed to CANCELLED.

Alternatives
------------

* To use Congress to automatically trigger audits when some conditions are met.
* To use a cronjob which triggers new audit regularly via python-watcherclient.

Data model impact
-----------------

There must be new field in Audit model: integer 'period'. 'period' field has
3600 by default.

REST API impact
---------------

period's field has to be added as Audit attribute.

Security impact
---------------

None expected.

Notifications impact
--------------------

None expected.

Other end user impact
---------------------

Support for 'period' field must be added to the python-watcherclient and
to the watcher-dashboard.

Performance Impact
------------------

No specific performance impact is expected.

Other deployer impact
---------------------

No specific deployer impact is envisaged.

Developer impact
----------------

This will not impact other developers working on OpenStack.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Alexander Chadin <alexchadin>
Other contributors:
  Vladimir Ostroverkhov <Ostroverkhov>

Work Items
----------

* Add support for periodic_task decorator.
* Implement PeriodicAuditHandler that manages DefaultAuditHandler.
* Implement method 'execute' that runs audits periodically.
* Adapt API to support period field.
* Make some changes to python-watcherclient to add support for period argument.
* Add changes to watcher-dashboard to support CONTINUOUS type.
* Implement appropriate unit tests to test various scenarios.

Dependencies
============

There are no dependencies.

Testing
=======

Appropriate unit tests will be adapted to new changes.

Documentation Impact
====================

It will be necessary to add new content relating to this change.

References
==========

No references.

History
=======

No history.


.. _Strategies: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Administrator: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#administrator
.. _Audit: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit
.. _Action Plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Cluster: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#cluster