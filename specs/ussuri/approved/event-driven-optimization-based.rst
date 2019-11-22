..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===============================
Event-driven optimization based
===============================

https://blueprints.launchpad.net/watcher/+spec/event-driven-optimization-based


Problem description
===================

Watcher has provided ONESHOT and CONTINUOUS audit. ONESHOT audit executes the
optimization only once after being launched. CONTINUOUS audit executes the
optimization periodly. But there is no way to react to the changes of system,
for example an alarm event.

Use Cases
----------

As a user of Watcher, I want to execute optimization as soon as possible
when there are alarms in the system.


Proposed change
===============

Many monitor system, such as `aodh`_, can set `webhook`_ as alarm action,
a POST request will be sent if the alarm is trigered.
Watcher add the mechanism for receiving and handling alarm events.

Here is the summary processing:
User creates an event based audit, a new audit type, named EVENT, is needed.
Creating alarm with Watcher webhook and audit uuid in the monitor system
such as aodh.
When the alarm is trigered, Watcher will receive the event with audit uuid.
Watcher executes the audit and creates actionplan.

.. _aodh: https://docs.openstack.org/aodh/latest/admin/telemetry-alarms.html#event-based-alarm
.. _webhook: https://en.wikipedia.org/wiki/Webhook

Alternatives
------------

CONTINUOUS audit can be used to satisfy the purpose but this will increase the
workload.

Data model impact
-----------------

None

REST API impact
---------------

Add a new webhook API

* /v1/webhooks/{audit_ident}

  * Triggers an event based audit, audit_ident is uuid or name of the audit.
    Does not perform verification of authentication token.

  * Method type: POST

  * Normal http response code: 202(Accepted)

  * Expected error http response code: 400, 404(Not Found)

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
  licanwei

Work Items
----------

* Add a new audit type, named EVENT

* Add a new webhook API

* processing for event based audit


Dependencies
============

None


Testing
=======

* Unit tests for the new feature

Documentation Impact
====================

* Add documentation about how to use the new feature


References
==========

https://docs.openstack.org/aodh/latest/


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Ussuri
     - Introduced

