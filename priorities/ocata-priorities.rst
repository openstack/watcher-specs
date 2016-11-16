.. _ocata-priorities:

=========================
Ocata Project Priorities
=========================

List of priorities the Watcher drivers team is prioritizing in Ocata.

+--------------------------------------+----------------------+
| Priority                             | Owner                |
+======================================+======================+
| `Define Audit Scope`_                | `Alexander Chadin`_  |
+--------------------------------------+----------------------+
| `Graph Model`_                       | `Kevin Mullery`_     |
+--------------------------------------+----------------------+
| `Watcher Versionned objects`_        | `Vincent Francoise`_ |
+--------------------------------------+----------------------+
| `Automatic triggering Action Plans`_ | `Digambar Patil`_    |
+--------------------------------------+----------------------+
| `Limit Concurrent Actions`_          | `Joe Cropper`_       |
+--------------------------------------+----------------------+
| `Workload Characterization Grammar`_ | `Prashanth Hari`_    |
+--------------------------------------+----------------------+
| `Workload Characterization and QoS`_ | `Prashanth Hari`_    |
+--------------------------------------+----------------------+
| `Update Notifications`_              | `Vincent Francoise`_ |
+--------------------------------------+----------------------+
| `Notifications for audits`_          | `Vincent Francoise`_ |
+--------------------------------------+----------------------+
| `Description For Dynamic Action`_    | `Charlotte Han`_     |
+--------------------------------------+----------------------+
| `Stale Action Plan`_                 | `Li Canwei`_         |
+--------------------------------------+----------------------+
| `Audit tag in VM Metadata`_          | `Prashanth Hari`_    |
+--------------------------------------+----------------------+

.. _Vincent Francoise: https://launchpad.net/~vincent-francoise
.. _Edwin Zhai: https://launchpad.net/~edwin-zhai
.. _Prashanth Hari: https://launchpad.net/~hvprash
.. _Charlotte Han: https://launchpad.net/~hanrong
.. _Alexander Chadin: https://launchpad.net/~joker946
.. _Kevin Mullery: https://launchpad.net/~kmullery
.. _Digambar Patil: https://launchpad.net/~digambarpatil15
.. _Kevin Mullery: https://launchpad.net/~kmullery
.. _Joe Cropper: https://launchpad.net/~jwcroppe
.. _Li Canwei: https://launchpad.net/~li-canwei2


Define Audit Scope
------------------

Administrator will be able to provide a logical subset of resources
where Watcher will run the optimization. This subset will be based on
`Host aggregates`_ and `Availability Zones`_.

Graph Model
-----------

The graph based data model  would aggregate resource information for the
`Cluster`_ and allow for the effective representation of the topology
of workload deployments. Through this model graph analysis techniques could be
employed in the context of the `Strategy`_ definition.

Watcher Versionned objects
--------------------------

Make all Watcher objects support `oslo.versionnedobjects`_.

Automatic triggering Action Plans
---------------------------------

Administrator will be able to choose to run the `Action Plan`_ automaticaly
right after Watcher has run the `Audit`_.

Limit Concurrent Actions
------------------------

We propose a capability that limits the number of concurrent `Action`_
that can be in flight when a particular `Audit`_ is invoked.

Workload Characterization Grammar
---------------------------------

We should be able to characterize such workloads as input to Watcher for
ensuring Application QoS, placements and consolidation. We need to define
a grammar to describe those workloads.

Workload Characterization and QoS
---------------------------------

Based on the grammar defined earlier, we should be able to describe workload
characteristics and map them to applications. Then it would allow Watcher to
build optimization `Strategy`_ based on those characteristics.

Update Notifications
--------------------

We should update Watcher notifications system to be compliant with
`Nova Notifications`_.

Notifications for audits
------------------------

Now that all Watcher object are versionned, we need to update the `Audit`_
object logic to handle notifications.

Description For Dynamic Action
------------------------------

We should add the ability to submit a description of each `Action`_ that
can append in an `Action Plan`_.

Stale Action Plan
-----------------

We should add a new state for `Action Plan`_ to be able to set it as
superseded in case the `Cluster Data Model`_ has changed or an event happened
that invalidate all previous `Action Plan`_.

Audit tag in VM Metadata
------------------------

As watcher runs audits to achieve a `Goal`_, there should be some way for the
application/VM owners to know that their VMs are under `Audit`_ and its
flagged before `Action Plan`_ execution.

.. _Cluster: http://docs.openstack.org/developer/watcher/glossary.html#cluster-definition
.. _Host Aggregates: http://docs.openstack.org/developer/nova/aggregates.html
.. _Availability Zones: http://docs.openstack.org/developer/nova/aggregates.html#availability-zones-azs
.. _oslo.versionnedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/
.. _Action Plan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan-definition
.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit-definition
.. _Action: http://docs.openstack.org/developer/watcher/glossary.html#action-definition
.. _Strategy: http://docs.openstack.org/developer/watcher/glossary.html#strategy-definition
.. _Nova Notifications: http://docs.openstack.org/developer/nova/notifications.html
.. _Cluster Data Model: http://docs.openstack.org/developer/watcher/glossary.html#cluster-data-model
.. _Goal: http://docs.openstack.org/developer/watcher/glossary.html#goal
