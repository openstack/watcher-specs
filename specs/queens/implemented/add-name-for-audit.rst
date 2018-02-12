..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=======================
Add a name for an audit
=======================

https://blueprints.launchpad.net/watcher/+spec/add-name-for-audit


Problem description
===================
It is not easy to tell the audits apart just by uuid for end users. If we add
a name for an audit, it is more friendly to end users.

Use Cases
---------
As an end user, I want to retrieve an audit by name.


Proposed change
===============

This spec is mainly to add a name for an audit, so it will be easy
for users to retrieve an audit.

* To watcherclient/watcher-api:
  User can show/delete/update an audit by name.
  Create an audit with a name. The audit name is not mandatory. If audit name
  was not provided, use a default name. The default name is made of strategy
  or audittemplate or goal name with current time.


* To DB:
  Add a new field in audit table to store the audit's name.
  New field in audit table,with unique attribute:
  name = Column(String(63), nullable=True)

* To notifications:
  Add audit name to AuditPayload, ActionPlanPayload

Alternatives
------------

None

Data model impact
-----------------

Yes, add a new field 'name' in audit table to store the audit's name.

REST API impact
---------------

The following API's will be changed. The parameter 'audit' now can be used
to GET, DELETE or PATCH one audit either by UUID or by name of the audit.
* ``GET /v1/audits``
* ``DELETE /v1/audits``
* ``PATCH /v1/audits``

The return value to Audit APIs will be changed. Add 'name' field
into audit object of below return value types.
* AuditCollection
* Audit

Security impact
---------------
None

Notifications impact
--------------------

Yes, it will add audit name to AuditPayload, ActionPlanPayload

Other end user impact
---------------------

It may impact watcher-dashboard.

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
sue

Work Items
----------
* Add name for audit, changes for python-watcherclient
* Add name for audit, changes for watcher api/db
* Add name for audit, update audit notifications and API references

Dependencies
============

None

Testing
=======

Unit test

Documentation Impact
====================

Yes, two docs will be updated.

* Notifications in Watcher
  https://docs.openstack.org/developer/watcher/dev/notifications.html

* API References
  https://docs.openstack.org/developer/watcher/#api-references


References
==========

None

History
=======

None

