..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=======================
Zone migration strategy
=======================

https://blueprints.launchpad.net/watcher/+spec/zone-migration-strategy

There are thousands of physical servers and storage running various kinds of
workloads in the cloud system. Operator have to migrate instances and
volumes for hardware maintenance once a quarter or so.
It requires operator to watch workloads, choose instances and volumes and
migrate them efficiently with minimum downtime.
Watcher can be used to do this task automatically.

Problem description
===================

It is hard for operator to migrate many instances and volumes efficiently
with minimum downtime for hardware maintenance.

Use Cases
----------

* As an operator, I want Watcher to migrate many instances and volumes
  efficiently with minimum downtime automatically.

Proposed change
===============

Add `Goal`_ "Hardware maintenance". The goal is to migrate instances and
volumes on a set(called "Zone" in this spec) of compute nodes and storage.

Add eight `Efficacy Indicator`_.

* LiveInstanceMigrateCount

  The number of instances should be live migrated

* PlannedLiveInstanceMigrateCount

  The number of instances planned to live migrate

* ColdInstanceMigrateCount

  The number of instances should be cold migrated

* PlannedColdInstanceMigrateCount

  The number of instances planned to cold migrate

* VolumeMigrateCount

  The number of detached volumes should be migrated

* PlannedVolumeMigrateCount

  The number of detached volumes planned to migrate

* VolumeUpdateCount

  The number of attached volumes should be updated

* PlannedVolumeUpdateCount

  The number of attached volumes planned to update

Add `Efficacy Specification`_ associated with the goal.
The efficacy specification has four global efficacy indicators.

* live_instance_migrate_ratio

  Ratio of planned live migrate instances to instances should be live
  migrated.
  The result of PlannedLiveInstanceMigrateCount / LiveInstanceMigrateCount

* cold_instance_migrate_ratio

  Ratio of planned cold migrate instances to instances should be cold
  migrated.
  The result of PlannedColdInstanceMigrateCount / ColdInstanceMigrateCount

* volume_migrate_ratio

  Ratio of planned detached volumes to volumes should be migrated.
  migrate.
  The result of PlannedVolumeMigrateCount / VolumeMigrateCount

* volume_update_ratio

  Ratio of planned attached volumes to volumes should be updated.
  The result of PlannedVolumeUpdateCount / PlannedVolumeUpdateCount

Add `Strategy`_ "Zone migration".
The strategy gets compute node and storage pool names given by input
parameter, and gets instances and volumes on them from cluster data model.
After that, the strategy prioritizes instances and volumes respectively
by the following list given by input parameter.

* project

* compute_node

* storage_pool

* compute

  The strategy chooses instances in descending order of one of the following:

  * vcpu_num

  * mem_size

  * disk_size

  * created_at

* storage

  The strategy chooses volumes in descending order of one of the following:

  * size

  * created_at

For example, If the following input parameters is given::

    "priority": {
        "project": ["pj1"],
        "compute_node": ["compute1", "compute2"],
        "compute": ["cpu_num"],
        "storage_pool": ["pool1", "pool2"],
        "storage": ["size"]
    }

And we have list of instances and volumes as the followings.

instances::

    {"project": "pj1", "node":"compute2", "cpu_num": 1, "memory_size": 4}
    {"project": "pj2", "node":"compute1", "cpu_num": 1, "memory_size": 2}
    {"project": "pj1", "node":"compute1", "cpu_num": 2, "memory_size": 3}
    {"project": "pj2", "node":"compute1", "cpu_num": 1, "memory_size": 1}

volumes::

    {"project": "pj1", "node":"pool1", "size": 3, "created_at": 2017-02-25}
    {"project": "pj1", "node":"pool1", "size": 3, "created_at": 2017-02-26}
    {"project": "pj2", "node":"pool1", "size": 5, "created_at": 2017-02-25}
    {"project": "pj1", "node":"pool2", "size": 3, "created_at": 2017-02-25}

Instances are prioritized as the following::

    {"project": "pj1", "node":"compute1", "cpu_num": 2, "memory_size": 3}
    {"project": "pj1", "node":"compute2", "cpu_num": 1, "memory_size": 4}
    {"project": "pj2", "node":"compute1", "cpu_num": 1, "memory_size": 2}
    {"project": "pj2", "node":"compute1", "cpu_num": 1, "memory_size": 1}

Volumes are prioritized as the following::

    {"project": "pj1", "node":"pool1", "size": 3, "created_at": 2017-02-25}
    {"project": "pj1", "node":"pool1", "size": 3, "created_at": 2017-02-26}
    {"project": "pj2", "node":"pool1", "size": 5, "created_at": 2017-02-25}
    {"project": "pj1", "node":"pool2", "size": 3, "created_at": 2017-02-25}

The strategy migrates all chosen volumes first by volume_migrate
action. Then the strategy migrates all chosen instances by migrate action.
Destination can be given by input parameter.

If volume is attached to an instance, the instance can be migrated
just after attached volume is migrated. Because they should be near place
for performance reason. This behavior is configurable.

The strategy uses weights planner that is the planner by default which has
the number of actions to be run in parallel on a per action type basis.
In addition to that, the strategy has the number of actions to be run in
parallel per node or pool. The number is given by the input parameter.

The strategy gets volumes and instances from prioritized ones and migrates
them which are limited to the number of volumes and instances to
each number of parallelization per host and the number of parallelization
per action in weight planner.

The input parameters are the followings::

    compute_nodes": [
        {
            "src_node": "cen-cmp02",
            "dst_node": "cen-cmp01"
        },
        ......
    ],
    "storage_pools": [
        {
            "src_pool": "cen-cmp02@lvm#afa",
            "dst_pool": "cen-cmp01@lvm#afa",
            "src_volume_type": "afa",
            "dst_volume_type": "afa"
        },
        ........
    ],
    "parallel_per_node": 2,
    "parallel_per_pool": 2,
    "priority": {
        "project": ["pj1", "pj2"],
        "compute_node": ["compute1", "compute2"],
        "storage_pool": ["pool1", "pool2"],
        "compute": ["cpu_num", "memory_size"],
        "storage": ["size"]
    }
    "with_attached_volume": false


Alternatives
------------

Operator migrates instances and volumes manually one by one.

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
  <nakamura-h>

Other contributors:
  <adi-sky17>

Work Items
----------

* Implement goal "Hardware maintenance"

* Implement efficacy indicator

* Impement efficacy specification

* Implement strategy "Zone migration"

  * Filters for prioritizing volumes and instances to be migrated

  * Parallel number controller

  * Migrating volumes and instances by actions logic

Dependencies
============

* https://blueprints.launchpad.net/watcher/+spec/volume-migrate-action
* https://blueprints.launchpad.net/watcher/+spec/cinder-model-integration
* https://blueprints.launchpad.net/watcher/+spec/multiple-global-efficacy-indicator

Testing
=======

* Unit and tempest tests are added.

Documentation Impact
====================

Strategy documentation is added.

References
==========

* https://www.youtube.com/watch?v=_6kB1NTob8o

History
=======

None

.. _Goal: https://docs.openstack.org/watcher/latest/glossary.html#goal
.. _Efficacy Indicator: https://docs.openstack.org/watcher/latest/glossary.html#efficacy-indicator
.. _Efficacy Specification: https://docs.openstack.org/watcher/latest/glossary.html#efficacy-specification
.. _Strategy: https://docs.openstack.org/watcher/latest/glossary.html#strategy
