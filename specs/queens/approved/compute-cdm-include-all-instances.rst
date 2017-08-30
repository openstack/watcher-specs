..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================================
compute CDM include all instances
==================================

https://blueprints.launchpad.net/watcher/+spec/compute-cdm-include-all-instances


Problem description
===================
When building compute CDM, we will exclude the instances excluded by the
scope. It has terrible impact to Watcher.

To workload balance and server consolidation, the excluded instances in
the scope are not added into the workload. So it would get incorrectly
workload of the compute nodes, and execute unreasonbale migrations.

To server consolidation, it would disable the nodes which still have
excluded instances running.


Use Cases
---------
As an end user, I want Watcher to take excluded instances into account
during workload calculations but not migrate excluded instances.


Proposed change
===============

Watcher should have a whole scope of the cluster, include all instances.
So it would get the correct workload of the nodes, and make the correct
optimization.

Compute CDM in Watcher should has a whole scope, include all instances.
It needs to be clear which instances are exclude and which are not.

* We can add "watcher_exclude" field to "Instance" resource to distinguish
  them, as following.

  class Instance(compute_resource.ComputeResource):
    fields = {
        "watcher_exclude": wfields.BooleanField(default=False),
        "state": wfields.StringField(default=InstanceState.ACTIVE.value),
        ...

    }

  When building compute CDM, set the 'watcher_exclude' flag 'True'
  if the instance is excluded by the scope.


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

* Add and identify excluded instances in compute CDM
* Adjust workload balance and server consolidation, when calculating
  workload of the compute nodes and generating solutions

Dependencies
============

Testing
=======

Unit test

Documentation Impact
====================

None

References
==========

https://docs.openstack.org/watcher/latest/glossary.html#cluster-data-model-definition

History
=======

None

