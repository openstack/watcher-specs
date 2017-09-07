..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Storage Capacity Balance Strategy
==========================================

https://blueprints.launchpad.net/watcher/+spec/storage-capacity-balance

As of now, Watcher optimizes only compute nodes.
Storage optimization is also an important feature for centralized storage
(non distributed storage).

This spec will add Storage Capacity Balance Strategy to balance the
storage capacity, which can be also considered a way to balance the
storage workload. And we can use existing goal(workload_balancing) and
action(volume_migrate) for this storage capacity balance.

Problem description
===================

In current Data Center, the capacity of storage back-end may be not balanced,
some are extremely high, some are idle. This situation will degrade the
performance of I/O Read/Write, which will finally affect the QoS.
This problem can be solved by storage capacity balance strategy.

This strategy migrates volumes based on the capacity utilization of the cinder
pools. It makes decision to migrate a volume whenever a pool's capacity
utilization % is higher than the specified threshold. The migration of a
volume should make the capacity utilization of the pool where it locates
lower than the storage capacity utilization threshold.

Use Cases
----------

As an administrator, I want to be able to trigger an audit that controls the
storage capacity utilization below a certain threshold.

Proposed change
===============

* Extend base strategy classes to add one new strategy - " Storage Capacity
  Balance Strategy"

* Use Cinder client to get all volumes with status in available or in-use
  and no snapshots, and to get all pools except the pools listed as
  exclude_pools in the configuration file.

* Group volume pools into two categories: underload or overload pools
  according to threshold:

  .. code-block:: python

      under_pools = list(filter(lambda p: float(p.total_capacity_gb) -
      float(p.free_capacity_gb) < float(p.total_capacity_gb) * threshold, pools))

      over_pools = list(filter(lambda p: float(p.total_capacity_gb) -
      float(p.free_capacity_gb) >= float(p.total_capacity_gb) * threshold, pools))

* Determine migrate_volumes, source pools and destination pools based on some
  factors:

  * whether a volume is mounted to a VM

  * volume size,

  * whether a volume is a mirrored volume

  * priority

Alternatives
------------

None

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
  <yumeng-bao>,<li-canwei2>

Work Items
----------

1. Define proper threshold

2. Write the execute function to locate pool overloaded

3. Function to generate actions:volume_migrate or volume_retype.

Dependencies
============

None

Testing
=======

Unit and functional test are needed.

Documentation Impact
====================

Add docs on how to use this strategy.

References
==========

None

History
=======

None
