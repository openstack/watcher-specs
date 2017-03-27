..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================================
Integrate storage (cinder) information in the model
===================================================

https://blueprints.launchpad.net/watcher/+spec/cinder-model-integration


Problem description
===================

As of now, Watcher only provides compute data model. Watcher needs storage data
model for optimizing storage provided by Cinder.

Use Cases
----------

* As a developer, I want to develop storage optimization strategy using storage
  data model.

* As as developer, I want to develop zone migration strategy using storage
  data model.

Proposed change
===============

This spec adds storage data model separate from compute data model.
Since Cinder backend has many pools, physical layer composed of backends and
it's pools. Backend information can be retrieved by python-cinderclient Service
resource. The model has host, zone, status, and state attributes of Service
resource. For using Multi backends feature, volume type is also needed. Volume
type information can be retrieved by python-cinderclient VolumeType resource.

Pool information can be retrieved by python-cinderclient Pool resource.
The model has name, total_volumes, total_capacity_gb, free_capacity_gb and
provisioned_capacity_gb and allocated_capacity_gb attributes of Pool resource.
Virtual_fee is also element of the model which is not retrieved
by python-cinderclient, but retrieved from cinder notification.

Virtual layer is Cinder volume. Volume information can be retrieved by
python-cinderclient Volume resource. The model has id, name, size, status,
attachements, snapshot_id, project_id and metadata attributes of Volume
resource.

In order to maintain consistency of the model, notification endpoint to consume
all needed cinder notifications will be added:

CapacityNotificationEndpoint

  This consumes the notification emitted in _publish_service_capabilities
  method periodically in cinder/manager.py from cinder-scheduler service.

  Payload is defined as return value of _usage_from_capacity method
  in cinder.volume.utils.py.

  Filter_rule is publisher_id equals r'capacity.*' and event_type equals
  'capacity_pool'.

  This endpoint updates pool information:

  ======================== ========================
  pool element             notification payload
  ======================== ========================
  name                     name_to_id
  total_volumes            None
  total_capacity_gb        total
  free_capacity_gb         free
  provisioned_capacity_gb  provisioned
  allocated_capacity_gb    allocated
  virtual_free             virtual_free
  ======================== ========================

  Total_volumes is not included in notification payload so that it is
  calculated when updating pool information.


Notifications for updating volume information are emitted in
cinder/volume/manager.py from cinder-volume service.
Payload is defined as return value of _usage_from_volume method in
cinder.volume.utils.py.

VolumeCreateEnd

  Filter_rule is publisher_id equals r'volume.*' and event_type equals
  'volume.create.end'.

  This endpoint creates an element of virtual layer under the pool element with
  the condition that host included in publisher_id equals pool name:

  ======================== ========================
  volume element           notification payload
  ======================== ========================
  id                       volume_id
  name                     display_name
  size                     size
  status                   status
  attachements             volume_attachment
  snapshot_id              snapshot_id
  project_id               tenant_id
  metadata                 volume_metadata
  ======================== ========================


VolumeDeleteEnd

  Filter_rule is publisher_id equals r'volume.*' and event_type equals
  'volume.delete.end'.

  This endpoint deletes the element of virtual layer with the condition
  that volume_id equals id.


VolumeUpdateEnd

  Filter_rule is publisher_id equals r'volume.*' and event_type equals
  'volume.update.end'.

  This endpoint updates the element of virtual layer with the condition
  that volume_id equals id:

  ======================== ========================
  volume element           notification payload
  ======================== ========================
  name                     display_name
  size                     size
  status                   status
  attachements             volume_attachment
  snapshot_id              snapshot_id
  project_id               tenant_id
  metadata                 volume_metadata
  ======================== ========================


VolumeAttachEnd

  Filter_rule is publisher_id equals r'volume.*' and event_type equals
  'volume.attach.end'.

  This endpoint updates the element of virtual layer with the condition
  that volume_id equals id. The attributes updating are the same as
  VolumeUpdateEnd.


VolumeDetachEnd

  filter_rule is publisher_id equals r'volume.*' and event_type equals
  'volume.detach.end'.

  This endpoint updates the element of virtual layer with the condition
  that volume_id equals id. The attributes updating are the same as
  VolumeUpdateEnd.


VolumeResizeEnd

  Filter_rule is publisher_id equals r'volume.*' and event_type equals
  'volume.resize.end'.

  This endpoint updates the element of virtual layer with the condition
  that volume_id equals id. The attributes updating are the same as
  VolumeUpdateEnd.


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

Notification endpoint to consume cinder notifications will be added.

Other end user impact
---------------------

None

Performance Impact
------------------

Watcher stores data model in memory. Watcher-decision-engine may need more
physical memory.

Other deployer impact
---------------------

The following is added in setup.cfg.

::

   [entry_points]
   watcher_cluster_data_model_collectors =
       storage = watcher.decision_engine.model.collector.cinder:CinderClusterDataModelCollector

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

* Add storage data model
* Add storage data model entry point in setup.cfg
* Add _storage_model instance variable and storage_model method with property
  decorator to BaseStrategy class
* Add notification endpoint for updating storage deta model


Dependencies
============

None


Testing
=======

Unit tests should be updated.


Documentation Impact
====================

Architecture documentation will be updated.


References
==========

* https://blueprints.launchpad.net/watcher/+spec/zone-migration-strategy


History
=======

None
