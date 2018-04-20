..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=======================
Noisy Neighbor Strategy
=======================

https://blueprints.launchpad.net/watcher/+spec/noisy-neighbor-strategy

This spec describes a new strategy that identifies and migrates a Noisy
Neighbor, which is a lower priority VM that negatively affects Last Level
Cache (LLC) of a higher priority VM when located on the same host.


Problem description
===================

Noisy neighbor is a big problem in multi-tenant clouds. Some lower priority
VMs can negatively affect performance on higher priority VMs by monopolizing
CPU, I/O, and network bandwidth. There are already strategies to cover some of
them like CPU utilization as well as algorithm using a threshold for cache
occupancy as an indicator to identify a noisy neighbor. These algorithms are
too simple and do not take into consideration the interaction between VMs
including the performance impact if any as well as the VMs' relative priority
to each other. For example a VM could use 50% cache occupancy and it could be
fine. It all depends on the VM's priority. This algortihm utilizes IPC, LLC
and VMs' relative priorities.

LLC(Last Level Cache), or L3 cache in X86, is critical and limit system level
resource shared by all apps or VMs on the node. If one VM occupy most of L3
cache, other VMs on the node likely starve without enough L3 cache thus poor
performance.


Use Cases
---------

As an openstack operator, I need to find noisy neighbor VMs that affect my
high priority VMs, and migrate them to another node that has no noisy negihbor
issues.


Proposed change
===============

* Add one new goal - "Noisy Neighbor migration"

* Extend base strategy classes to add one new strategy - "Noisy Neighbor
  solution"

* Use Ceilometer client to get following metrics for detecting LLC noisy
  neighbor:

  * cpu_l3_cache -- LLC occupancy of a VM

* Algorithm to detect Noisy Neighbor:

  * Monitor L3 cache of all VMs in order of their "watcher-priority", that is
    set in VM metadata.
    Example: L3 cache of VM with watcher-priority as "1" will be monitored
    before VM with watcher-priority as "8".

  * If L3 cache of a VM goes down by more than the threshold, mark it as
    high priority. Then start monitoring L3 cache of VMs in reverse order of
    their "watcher-priority"

  * If L3 cache of a VM (VMs to be searched in reverse order of
    "watcher-priority") increases by the threshold, then the VM is a noisy
    neighbor.

  * Look for a node with no Noisy Neighbor issue and migrate the noisy VM
    there.


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

Querying metrics will probably cause small performance drop when running the
strategy.

Other deployer impact
---------------------

To enable LLC metric, latest Intel server with CMT support is required.
Also collectd is required to gather LLC metric data.

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <prudhvi-rao-shedimbi>


Work Items
----------

1. Define proper threshold for IPC and LLC

2. Write the execute function to locate the noisy neighbor

3. Choose target node for live migration.

Dependencies
============

* https://pypi.org/project/libvirt-python

Testing
=======

Unit and functional test are needed.


Documentation Impact
====================

Add docs on how to use this strategy.


References
==========

http://www.intel.com/content/www/us/en/architecture-and-technology/resource-director-technology.html


History
=======

None

