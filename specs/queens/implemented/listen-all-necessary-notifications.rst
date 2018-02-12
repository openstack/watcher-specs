..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================================================
listen to all necessary notifications for updating Compute CDM
==============================================================

https://blueprints.launchpad.net/watcher/+spec/listen-all-necessary-notifications


Problem description
===================

In Watcher, it firstly builds compute CDM by collecting nova compute resource,
later updates the compute CDM by listening to nova notifications.
It has listened to following nova events,

* service.update
* instance.update
* instance.delete.end
* compute.instance.update
* compute.instance.create.end
* compute.instance.delete.end
* compute.instance.live_migration.post.dest.end

In one cloud env, there would be many solutions, which would make the compute
resource strongly relocated, such as 'auto-scaling' solution and 'compute-ha'
solution. If Watcher doesn't listen to all the notifications which represent
that nova compute resource changes, the compute CDM will become stale easily
and watcher would not provide efficient solution.

Use Cases
---------

As an OpenStack administrator, I want Watcher still to work steady when other
projects make the compute resources changed.

Proposed change
===============

Following events also represent that nova compute resource changes. Watcher
needs to listen to the following notifications and update the compute model.

* compute.instance.rebuild.end
* compute.instance.resize.confirm.end

Notification 'compute.instance.rebuild.end' represents the 'evacuate' action
of one instance is finished, while notification
'compute.instance.resize.confirm.end' represents the 'resize' action of one
instance is finished and confirmed by the user. Once Watcher listens to such
notifications, it needs to update the instances mapping in the compute model.

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
sue

Work Items
----------

* listen to 'compute.instance.rebuild.end' event
* listen to 'compute.instance.resize.confirm.end' event

Dependencies
============

None

Testing
=======

Unit test

Documentation Impact
====================

None

References
==========

None

History
=======

None
