..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===========================================
Host maintenance strategy disable migration
===========================================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/host-maintenance-strategy-disable-migration

Problem description
===================

Host maintenance is a migration strategy designed for maintaining a compute
node. It triggers either live or cold migration for all instances on the node,
assuming that both migration methods are available. However, this may not apply
to deployments where live or cold migration is not supported.

Use Cases
---------

When using host maintenance strategy:

- As a Cloud Administrator, if live migration is supported in my
  OpenStack deployment. I want to apply live migration to the instance.
- As a Cloud Administrator, if live migration is not supported in my
  OpenStack deployment, but cold migration is supported.
  I want to apply cold migration to the instance.
- As a Cloud Administrator, if both live migration cold migration are
  not supported in my OpenStack deployment.
  I want to stop the instance.

Proposed change
===============

Estimated changes are going to be in the following places:

* Host maintenance strategy

  * Input parameters **disable_cold_migration** and **disable_live_migration**
    to disable the migration.

  * If **disable_live_migration** is given:

    * This tell the strategy the live migration shouldn't be considered
      during planning.
    * The instances in active status will be stopped.
    * If **disable_cold_migration** is not given,
      migrate all the SHUTOFF instances,
      including the instances stopped by previous operation.

  * If **disable_cold_migration** is given,
    this tell the strategy the cold migration shouldn't be considered
    during planning.

* New stop actions in applier

  * Action to stop the instance

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

Two new input parameters for host maintenance strategy.

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

Two new input parameters for host maintenance strategy,
the behavior is expected as the same if no parameters
are provided, so no breaking change.

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
  <jneo8>

Work Items
----------

1. New applier action to stop the instance.

2. Modify the function which creates migration action for instance.

Dependencies
============

* https://specs.openstack.org/openstack/watcher-specs/specs/queens/approved/cluster-maintenance-strategy.html

Testing
=======

* Unit tests on the Watcher Decision Engine and Applier.

* Integration tests

  * Launch an audit with the **disable_live_migration**
    input parameter enabled.
  * Launch an audit with the **disable_cold_migration**
    input parameter enabled.
  * Launch an audit with both **disable_live_migration**,
    **disable_cold_migration** input parameters enabled.

Documentation Impact
====================

Need to update `Host Maintenance Strategy documentation`_.

References
==========

None

History
=======

None

.. _Host Maintenance Strategy documentation: https://docs.openstack.org/watcher/latest/strategies/host_maintenance.html
