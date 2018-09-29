..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================================
Update DataModel by Nova Notifications
======================================

https://blueprints.launchpad.net/watcher/+spec/update-datamodel-by-nova-notifications


Problem description
===================

Watcher has a Compute DataModel(CDM) which includes all the info about
instances and nodes. Nova will emit notifications when instances or nodes
change their states. So Watcher can consume Nova notifications to update
its CDM. Now Watcher just consider several notifications, there are more
notifications need to be used, such as instance poweron/poweroff.

Use Cases
----------

As a Watcher developer, I want to consume Nova notifications to update CDM.


Proposed change
===============

We define a functional dict to map the notification and CDM.
for example:

.. code-block:: python

    def InstanceDelete(payload):
        pass

    def InstanceUpdate(payload):
        pass

    funcdict = {
        'instance.delete.end': InstanceDelete,
        'instance.update': InstanceUpdate,
        }

    def updateCDM(instancetype, payload):
        func = funcdict.get(instancetype)
        if func:
            func(payload)


We can classify notifications based on the impact on CDM:

* Add or update instance in CDM:

  * instance.create.end

  * instance.lock

  * instance.unlock

  * instance.pause.end

  * instance.power_off.end

  * instance.power_on.end

  * instance.resize_confirm.end

  * instance.restore.end

  * instance.resume.end

  * instance.shelve.end

  * instance.shutdown.end

  * instance.suspend.end

  * instance.unpause.end

  * instance.unrescue.end

  * instance.unshelve.end

  * instance.rebuild.end

  * instance.rescue.end

  * instance.update

  * instance.live_migration_force_complete.end

  * instance.live_migration_post_dest.end

* Remove instance from CDM

  * instance.delete.end

  * instance.soft_delete.end

* Add or update node in CDM

  * service.create

  * service.update

* Remove node from CDM

  * service.delete

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

Watcher will start to consume more notifications from Nova.

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
  <licanwei>


Work Items
----------

- List Nova notifications that Watcher consumes to upate CDM.
- Implement the code that update CDM from notification payload.


Dependencies
============

None


Testing
=======

Unit tests should be added.

Documentation Impact
====================

None


References
==========

* https://docs.openstack.org/nova/latest/reference/notifications.html#existing-versioned-notifications


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Stein
     - Introduced

