..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================
Improve Compute Data Model
==========================

https://blueprints.launchpad.net/watcher/+spec/improve-compute-data-model


Problem description
===================

The fields(vcpus, memory and disk_capacity) in the Watcher ComputeNode
correspond to the fields(vcpus, memory_mb and local_gb) in Nova API
`list-hypervisors-details`_. Unfortunately, these fields do not take
allocation ratios used for overcommit into account so there may be
disparity between this and the used count.

.. _list-hypervisors-details: https://developer.openstack.org/api-ref/compute/?expanded=list-hypervisors-details-detail#list-hypervisors-details

Use Cases
----------

As a Watcher user, I wish Watcher can work correctly in the case of
overcommit resources(cpu, memory and disk).


Proposed change
===============

Now Watcher had added `Placement helper`_. Watcher can get resource
information such as total, allocation ratio and reserved information
from API `list resource provider inventories`_.

Watcher ComputeNode
-------------------

We need to add some fields to the Watcher ComputeNode:

* vcpu_reserved: The amount of cpu a node has reserved for its own use.
* vcpu_ratio: CPU allocation ratio.
* memory_mb_reserved: The amount of memory a node has reserved for
  its own use.
* memory_ratio: Memory allocation ratio.
* disk_gb_reserved: The amount of disk a node has reserved for its own use.
* disk_ratio: Disk allocation ratio.

We can calculate the total resource capacity through the total, reserved and
allocation ratio.

The formula:
vcpu capacity = (vcpus-vcpu_reserved)*vcpu_ratio

For example, for vcpu resource with:

::

  vcpus = 8
  vcpu_reserved = 2
  vcpu_ratio = 5.0

The vcpu capacity is (8 - 2) * 5.0 = 30.

We also add some new propeties to the Watcher ComputeNode:

* vcpu_capacity: The amount of vcpu, take allocation ratio into account,
  but do not include reserved.
* memory_mb_capacity: The amount of memory, take allocation ratio into
  account, but do not include reserved.
* disk_gb_capacity: The amount of disk, take allocation ratio into
  account, but do not include reserved.

.. _Placement helper: http://specs.openstack.org/openstack/watcher-specs/specs/train/approved/support-placement-api.html
.. _list resource provider inventories: https://developer.openstack.org/api-ref/placement/?expanded=list-resource-provider-inventories-detail#list-resource-provider-inventories

Compute Data Model
------------------

CDM(Compute Data Model) will be built when creating audit and updated
when receiving Nova notifications. So when building and updating CDM
we need to get resource information from Placement API.

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

* Add new fields to Watcher ComputeNode
* Update compute collector
* Update the processing about Nova notifications


Dependencies
============

None


Testing
=======

Add unit test


Documentation Impact
====================

None


References
==========

https://developer.openstack.org/api-ref/compute/

https://developer.openstack.org/api-ref/placement/


History
=======


.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced

