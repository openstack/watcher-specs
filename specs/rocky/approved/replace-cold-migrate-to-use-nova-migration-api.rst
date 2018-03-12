..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

================================================
Replace cold migration to use Nova migration API
================================================

https://blueprints.launchpad.net/watcher/+spec/replace-cold-migrate-to-use-nova-migration-api


Problem description
===================

Currently watcher implements instance cold migration by it's own for
specifying destination node.
The implementation includes instance creation. Since administrator runs
watcher API, instance migrates to admin project.

Use Cases
----------

Migrate action executes instance cold migration if migration_type is cold.


Proposed change
===============

Since v2.56, Nova `migrate Server(migrate Action)`_ API has host option.
By replacing watcher_non_live_migrate_instance method in common/nova_helper.py
to use the API, we can simply solve the problem.

Alternatives
------------

It may be the alternative to create instance by temporary user in the
project where instance is in.
But this solution remains quota problem. During temporary user lives and
reached quota limit, new user can not be created.

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

We may expect cold migration becomes faster because current implementation
calls many Nova and Neutron API.


Other deployer impact
---------------------

* Administrator can see migration by watcher using Nova List Migrations API.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <nakamura-h>

Other contributors:
  <None>

Work Items
----------

* Replace watcher_non_live_migrate_instance method
  in common/nova_helper.py to use Nova migrate Server(migrate Action) API.


Dependencies
============

None


Testing
=======

We should expect current test code can test this replacement.


Documentation Impact
====================

None


References
==========

.. _migrate Server(migrate Action): https://developer.openstack.org/api-ref/compute/#migrate-server-migrate-action
