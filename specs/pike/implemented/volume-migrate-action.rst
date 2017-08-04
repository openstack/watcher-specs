..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================
Volume migrate action
=====================

https://blueprints.launchpad.net/watcher/+spec/volume-migrate-action


Problem description
===================

As of now, Watcher only provides Nova migrate action. Watcher needs cinder
volume migrate action for optimizing storage provided by cinder.

Use Cases
----------
* As a developer, I want to develop storage optimization strategy which
  migrates cinder volume.

* As a developer, I want to develop zone migration strategy which migrates
  cinder volume.

Proposed change
===============

This spec adds storage migrate action.

The schema is like the following::

    schema = Schema({
        'resource_id': str,  # should be a UUID
        'migration_type': str,  # choices -> "swap", "cold"
        'destination_node': str,
        'destination_type': str,
    })

Resource_id and migration_type are mandatory parameters.
Default migration_type is swap.

If migration_type is "cold", This action verifies that volume is detached
and has no snapshots. If false, WatcherException.Invalid exception with
the message "Invalid state for cold migration" is raised and the action
ends with FAILED state. If true, the action continues.

If destination_node is added, first check if volume type of source node
and destination node are the same. If true, this action migrates detached
volume of resource_id to destination_node by calling Cinder migration API.
If false, WatcherException.Invalid exception with the message
"Volume type must be same for migrating" is raised and the action ends
with FAILED state.

If destination_type is added, first check if volume type of source node
and destination node are different. If true, this action migrates detached
volume of resource_id to destination_type by calling Cinder retype API.
If false, WatcherException.Invalid exception with the message
"Volume type must be different for retyping" is raised and the action
ends with FAILED state.

If migration_type is "swap" then destination_type is required. If
destination_type has not been provided, WatcherException.Invalid exception
with the message "destination type is required when migration type is swap"
is raised.
Moreover, the action verifies that volume is attached and instance
status is active, paused, or resized. If false, WatcherException.Invalid
exception with the message "Invalid state for swapping volume" is raised
and the action ends with FAILED state. If true, the action swaps attached
volume of resource id. This action proceeds the following steps:

- create a temporary user in the project which created source volume
- create destination volume of destination_type by the temporary user
- swap volume from source volume to destination volume by using Nova
  Update a volume attachment API
- delete source volume
- delete the temporary user

Temporary user password is determined randomly for each user to reduce
security risk as much as possible.

The action execution diagram is below.

::

  if "migration_type" +------------->if "migration_type" +------>ERROR
  is 'cold'?              no         is 'swap'?              no
        +                                   +
        | yes                               | yes
        |                                   v
        |                            is "destination_type" +---->ERROR
        |                            given?                  no
        |                                   +
        |                                   |yes
        |                                   v
        v                            is volume attached
  is volume detached                 and instance is active
  and no snapshots? +----> ERROR     paused, or resized?    +--->ERROR
        +             no                    +                no
        |                                   | yes
        | yes                               v
        |                            5 steps described above
        |
        v
  is "destination_node"+------------>is "destination_type" +---->ERROR
  given ?                  no        given?                  no
        +                                   +
        | yes                               | yes
        |                                   |
        v                                   v
  is volume type                     is volume type
  the same?                          different?
        +---------------+                   +------------------+
        |               |                   |                  |
        | yes           | no                | yes              | no
        v               v                   v                  v
  call cinder migrate  ERROR         call cinder retype       ERROR


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

If migration_type is swap, temporary user password can be security risk.

Notifications impact
--------------------

None

Other end user impact
---------------------

If migration_type is swap, creation of temporary user or destination
volume may exceed quota and result in error.

Performance Impact
------------------

None

Other deployer impact
---------------------

Swap migration_type works for compute libvirt driver only.

The following is added in setup.cfg.

::

   [entry_points]
   watcher_actions =
       volume_migrate = watcher.applier.actions.storage_migration:VolumeMigrate

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <nakamura-h>

Work Items
----------

* Add volume migrate action
* Add volume migrate action entry point in setup.cfg

Dependencies
============

None

Testing
=======

Unit tests should be updated.


Documentation Impact
====================

Architecture documentation will be updated since action driver requests
cinder API by this spec.


References
==========

* https://developer.openstack.org/api-ref/compute/?expanded=#update-a-volume-attachment
* https://docs.openstack.org/cinder/latest/devref/migration.html

History
=======

None
