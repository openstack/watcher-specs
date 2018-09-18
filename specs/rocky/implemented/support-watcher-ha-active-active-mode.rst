..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================
Support Watcher HA active-active Mode
=====================================

https://blueprints.launchpad.net/watcher/+spec/support-watcher-ha-active-active-mode

Watcher Decision Engine and Applier currently don't support
HA active-active mode.


Problem description
===================

There is often more than one controller in the real environment.
Watcher Decision Engine and Applier are deployed on the controller.
Now there is only one active Watcher-decision-engine or Applier.
Otherwise Watcher Decision Engines will make duplicate actionplans for
CONTINUOUS audit. And we don't know which Applier is doing the actionplan.
Another problem is how to sync Data Models of Decision Engines to each other.
Now Decision Engine updates its Data Model based on notifications from Nova.
If there are many Decision Engines, we need to find a way to broadcast
notifications. One `solution`_ don't depend on notifications is to update
CDM before each audit.

Use Cases
----------

As an operator, I want to enable all Watcher-decision-engine and Applier on
all controllers.


Proposed change
===============

If we enable more than one Watcher Decision Engine, the question is how to
know the relation between Audit and Watcher Decision Engine.
We can add a new 'host' field to the Audit table to solve this question.
When we update the audit state from PENDING to ONGOING, we set the host
field to record the Watcher Decision Engine hostname.

So, the changes will include:

* Watcher Decision Engine CDM should consume notifications from Nova in
  broadcast mode to make CDMs synced.

* Add a new 'host' field to the audit table

* Add a new 'host' field to the actionplan table

* Record the host when updating the audit's state from PENDING to ONGOING

* Record the host when updating the actionplan's state from PENDING to ONGOING

* For CONTINUOUS audit, we need to check the host that running decision engine
  and recorded host value in audit table. If they are different, just skip the
  audit.

* When starting Applier process, if there are ONGOING actionplan with the
  same host, cancel these stale actionplans. Actions of these stale actionplans
  should also be marked as CANCELLED.

* Action Plan includes different resources which are represented in Actions.
  If user wants to run more than one action plan at the same time,
  Watcher should check whether new action plan's resources overlaps with
  already running one or not. If so, Watcher should prevent running of new
  Action Plan by raising appropriate error.

Alternatives
------------

None

Data model impact
-----------------

* Add a new 'host' filed in the audit table

* Add a new 'host' filed in the actionplan table

REST API impact
---------------

None

Security impact
---------------

None

Notifications impact
--------------------

Add 'host' field to AuditPayload, ActionPlanPayload

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  alexchadin
Other contributors:
  licanwei


Work Items
----------

* Add broadcast notifications for DE

* Update database to add a new field 'host'

* Record host when changing state from PENDING to ONGOING

* Add checking host for CONTINUOUS audit

* Check stale actonplans when starting Applier


Dependencies
============

None


Testing
=======

Unittest for each change.


Documentation Impact
====================

Appropriate documentation should be added with new HA
section.


References
==========

None


History
=======

None

.. _commit: https://review.openstack.org/#/c/551963
.. _solution: https://blueprints.launchpad.net/watcher/+spec/sync-datamodel-before-audit-execution
