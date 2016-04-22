..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Workload Based Migration Strategy
==========================================

https://blueprints.launchpad.net/watcher/+spec/workload-balance-migration-strategy

This spec proposes a new Watcher migration strategy based on the VM workloads
of hypervisors. This strategy makes decisions to migrate workloads to make the
total VM workloads of each hypervisor balanced, when the total VM workloads of
hypervisor reaches threshold.

Note: * VM workloads means how much CPUs the VM instance fully used, eg a VM
        instance has 4 CPUs, the VM workload range is [0.00 , 4.00].

      * This strategy is based on that all hosts have the same CPUs.

Problem description
===================

In current Data Center, VM workloads on each hypervisor may not balance, some
are extremely high, some are idle, which will reduce the cooling efficiency,
this strategy will balance the workloads when the CPU utilization of
hypervisor reaches threshold.

Use Cases
----------

As an administrator, I want to be able to trigger an audit that controls the
CPU utilization below a certain threshold.

In order to:

* balance the workloads on each hypervisor, make it close to average workload
  value of all hypervisors.

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

Watcher already has its decision framework, so this strategy should be a new
class which extend the base strategy class.

* Set the threshold in 2 steps: hard coded first, then through the template.
  see: https://blueprints.launchpad.net/watcher/+spec/optimization-threshold
  Threshold is the trigger value to start workload balancing.
  It can be the percentage of CPU utilization of hypervisor.

* Create a new Python class to extend the "BaseStrategy" class.

* Use the Nova objects framework to get free CPU/Memory/Disk of hypervisors.

* Use the Ceilometer client to get VM "cpu_util" to calculate the workloads.
  The time window is 5 minutes here, will be configurable as threshold.
  It uses ceilometer aggregation API to get the average value of "cpu_util".

* An algorithm to detect if the threshold of workloads has been reached, it
  will figure out the suitable VM to be moved, and it will filter the viable
  targets according to the free resource information of hypervisors from
  previous step and choose the one with lowest workloads. It will use
  select-destinations-filter when it is ready.
  It will also do some check to avoid the corner case, such as "ping pong".

Alternatives
------------

No alternative

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

There used to be some performance issues regarding the query of metrics from
the Ceilometer database. This is one of the reasons why it was rarely used in
production environment. These issues may now be solved thanks to an
abstraction layer which enables anybody to change the underlying metrics
storage backend easily.

There is a performance issue when you query the Nova DB to get CPU usage
metrics.

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
  <edwin-zhai>


Work Items
----------

1. function to calculate the total VM workloads of hypervisors.

2. function to filter hypervisors by Nova basic metrics(free CPU/Memory/Disk).

3. Rewrite execute function to add the algorithm to detect the threshold and
   to pick up the suitable VM to be moved and choose the target hypervisors,
   generate the solution.


Dependencies
============

* https://blueprints.launchpad.net/watcher/+spec/optimization-threshold

* https://blueprints.launchpad.net/watcher/+spec/select-destinations-filter

* http://docs.openstack.org/developer/python-novaclient/api.html

* https://blueprints.launchpad.net/watcher/+spec/get-goal-from-strategy


Testing
=======

Unit tests and functional test, will use a fake metrics set for running
functional test.


Documentation Impact
====================

A documentation explaining how to use this new optimization strategy.


References
==========

None

History
=======

None