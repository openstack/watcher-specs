..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===========================
Node Resource Consolidation
===========================

https://blueprints.launchpad.net/watcher/+spec/node-resource-consolidation


Problem description
===================

In the edge computing system, the edge nodes are distributed in different
locations. Although the total number of edge nodes may be large, the number
of edge nodes in each location is limited, so the resources(VCPU, memory)
are limited. An application scenario is to dynamically create VM(application)
processing service. After the processing is complete, the VM is deleted and
the resource is released. During this process(creating and deleting VM on
different nodes), resource fragments are generated. For example, if two nodes
each have two free VCPUs, even if the total VCPUs is enough, creating a VM
with four VCPUs will still fail.

Use Cases
----------

As a Watcher user, I wish Watcher provides a strategy which can eliminate
resource fragmentation by consolidating resources on nodes.


Proposed change
===============

* Add a new strategy: Node Resource Consolidation

* One input parameter: host_choice(specify/auto). This parameter
  determines how to select the server migration destination node.
  The value `auto` means that Nova schedular selects the destination node,
  and `specify` means the strategy specifies the destination.
  The default value is `auto`.

* The algorithm of this strategy:

  * Caculating the used resources of compute nodes
  * Sorting compute nodes by the used resources percent
  * Dividing compute nodes into source group and destination group.
    The process: For sorted compute nodes, from the one that uses least
    resources, if all servers can be migrated to other compute nodes,
    we put this node into source group, and other nodes into destination
    group. repeating this process until all compute nodes are placed in
    the source or destination group.
    For `continuous` audit, if there is server that had failed during previous
    actionplan, we should put this compute node to the destination group.
  * Creating strategy solution:
    If the parameter `host_choice` is `auto`, creating a migration action for
    each VM in the source group and compute nodes in source should be disabled
    before server migration and be enabled after finishing the migration.
    If the parameter `host_choice` is `specify`, the nodes in the destination
    group are sorted by free resources. Then, for each VM on the source node,
    select a node that is most suitable for the VM from the destination group
    as the destination node of the migration. Repeat this process (reordering
    the destination group by free resources each time), until all VMs have
    destination or there is insufficient resources.

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
  licanwei

Work Items
----------

* Add a new parameter `audit` to the method do_execute of strategy.
* Add the new strategy.


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

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced

