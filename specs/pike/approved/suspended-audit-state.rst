..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================
Suspended audit state
=====================

https://blueprints.launchpad.net/watcher/+spec/suspended-audit-state

Problem description
===================

If an audit with continuous mode needs to be stopped temporarily in order
to execute an audit and then restarted, it will have to be deleted
and recreated.

Use Cases
---------

* As an administrator, I want to suspend an audit with continuous mode to
  execute audit regularly for maintenance.

* As an administrator, I want to resume the audit with continuous mode to
  execute audit after maintenance.

Proposed change
===============

Currently, scheduler periodically picks up audit of **PENDING**, **ONGOING**
or **SUCCEEDED** state. Then audit's job named execute_audit is added to
scheduler. Execute_audit job first checks audit state. If state is
**CANCELLED**, **DELETED** or **FAILED**, audit's job is removed and
strategy is not executed.

This spec adds new audit state **SUSPENDED** and changes execute_audit's audit
state check condition. If state is **CANCELLED**, **DELETED**, **FAILED**
or **SUSPENDED**, audit's job is removed and strategy is not executed.
Otherwise, strategy is executed.

Since **SUSPENDED** is new audit state, audit state transition check when
updating audit state is also changed. **ONGOING** state can be changed to
**SUSPENDED**. **SUSPENDED** can be changed to **ONGOING** in reverse.

Alternatives
------------

* Delete the audit and create again.

* Currently, **ONGOING** state can be changed to **CANCELLED** state, but
  not be changed in reverse. If we can change from the **CANCELLED** state
  to **ONGOING** state, it is also an alternative.

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

None

Notifications impact
--------------------

None

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
  <nakamura-h>

Work Items
----------

* Add **SUSPENDED** in State class of watcher.objects.audit module.
* Update ContinuousAuditHandler that **SUSPENDED** is also inactive state.

Dependencies
============

None

Testing
=======

Unit tests and tempest tests should be updated.

Documentation Impact
====================

Need to update the **Audit State Machine** in the architecture documentation.

References
==========

None

History
=======

None
