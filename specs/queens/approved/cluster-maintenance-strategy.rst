..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================
Host maintenance strategy
==========================

https://blueprints.launchpad.net/watcher/+spec/cluster-maintaining

Problem description
===================

Sometimes we need to maintain compute nodes, update hardware or software,
and so on, without interrupting user's applications.

Use Cases
---------

As an openstack operator, sometimes I want to maintain one compute node
without interrupting user's applications.


Proposed change
===============
There will be a new goal and strategy for cluster-maintenance.

* Add one new goal - "Cluster Maintenance"
* Add one new strategy for this goal - "Host Maintenance"

The new strategy executes as follows

* First, get the compute node which needs maintenance. This input parameter
  is provided by the administrator. Call change_nova_service_state action
  to set the maintaining node in "maintaining" state (disabled with
  disable_reason  'watcher_maintaining').
* Then, call migrate action to migrate all instances on the maintaining node
  to other nodes. Migrate active instances use "live-migrate" and
  others use "cold-migrate". Calculate free cpus/memory/disk of a node
  to determine whether one instance or all instances from the maintaining node
  can migrate to.
  This strategy just consider how to migrate all instances of the
  maintaining node, further optimization rely on other strategies.
  There are two methods to migrate the instances of the maintaining node:
  Method No.1, migrate all instances on the maintaining node intensively to
  one unused host.The 'unused' host means disable but not power-off node
  for Watcher. If there are more than one "unused" hosts, choose one from
  them by random.
  (This method won't result in more VMs migration among other hosts.)
  Method No.2, just migrate all instances on the maintaining node dispersedly
  to other nodes.
  Method No.1 is priority. Only if Method No.1 fails, Method No.2 will
  execute. If both methods fail, this audit fails and raise exception with
  no solution produced.

After the maintenance finished, the administrator needs to activate the
maintaining node by cli 'nova service-enable' to change the node's state
from "maintaining" to "enabled" manually, which will make the compute node
rejoin into compute resource.

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

Primary assignee:sue

Work Items
----------

 * Add strategy and goal for cluster_maintenance
 * Update change_nova_service_state action, to make it available to
   maintain one compute node.

Dependencies
============

https://blueprints.launchpad.net/watcher/+spec/extend-node-status

Testing
=======

Unit tests

Documentation Impact
====================

A documentation explaining how to use this new optimization strategy.

References
==========

None

History
=======

None

