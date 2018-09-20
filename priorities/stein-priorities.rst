.. stein-priorities:

========================
Stein Project Priorities
========================

List of priorities the Watcher drivers team is prioritizing in Stein.

+-------------------------------------------------+-----------------------+
| Priority                                        | Owner                 |
+=================================================+=======================+
| `API Microversioning`_                          | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Watcher Planner Selector`_                     | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Define grammar for workload characterization`_ | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Bare metal node N+1 redundancy`_               | `Dao Cong Tien`_      |
+-------------------------------------------------+-----------------------+
| `Ironic notifications for bare metal DM`_       | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Update Data Model by Nova notifications`_      | `Li Canwei`_          |
+-------------------------------------------------+-----------------------+
| `Display Data Model of specified Audit`_        | `chenke`_             |
+-------------------------------------------------+-----------------------+
| `Add the start/end time for CONTINUOUS audit`_  | `Li Canwei`_          |
+-------------------------------------------------+-----------------------+
| `Audit scoper for baremetal data model`_        | `Yumeng Bao`_         |
+-------------------------------------------------+-----------------------+
| `Enhance watcher Applier engine`_               | `Li Canwei`_          |
+-------------------------------------------------+-----------------------+


.. _Alexander Chadin: https://launchpad.net/~joker946
.. _Li Canwei: https://launchpad.net/~li-canwei2
.. _Yumeng Bao: https://launchpad.net/~yumeng-bao
.. _Dao Cong Tien: https://launchpad.net/~tiendc
.. _chenke: https://launchpad.net/~chenker

API Microversioning
-------------------
We have to provide backward compatibility by adding API microversioning since
Watcher get new resources and their attributes during development cycles.

Watcher Planner Selector
------------------------
This component is responsible for selecting an appropriate `planner`_ for a
given `strategy`_ depending on several factors (e.g list of `actions`_ used by
the strategy or user request)

Define grammar for workload characterization
--------------------------------------------
As we run several workloads in a cloud, we should be able to characterize
such workloads as input to watcher for ensuring Application QoS, placements
and consolidation. An example of workload characterization is a weighted
combination of CPU, Memory or any other resource attributes like High IOPs,
Network latency etc.

Bare metal node N+1 redundancy
------------------------------
This proposes high availability/reliability feature to support Bare Metal Node
N+1 Redundancy based on data from Ceilometer.

When a bare metal node is failed due to hardware problem or is likely to be
failed due to a sign of hardware failure, this function allows to switch over
the node safely to another bare metal node in short time if the failed node is
booted from a volume.

Ironic notifications for bare metal DM
--------------------------------------
Update the bare metal data model by ironic notifications

Update Data Model by Nova notifications
---------------------------------------
Watcher consumes Nova notifications to update its Data Model. So far only
several notifications are used, there are many notifications need to be
consider, such as instance poweron/poweroff, they all change the state of
instance. Watcher should update the state of instance in the Data Model by
consuming appropriate Nova notifications that influence the state of instance
or compute.

Display Data Model of specified Audit
-------------------------------------
This blueprint will allow to display structure of Audit's Data Model. Data
Model stucture should be useful for operators who would like to know the set
of resources, which are also known as `scope`_, that are used by Audit. The
response can be represent as table in case of CLI and as graph model in case of
Watcher Dashboard.

Add the start/end time for CONTINUOUS audit
-------------------------------------------
Currently we can only set audit execution interval, but we can not set audit
start and end time. We need to increase the `audit`_ start and end time for
CONTINUOUS audit.

Audit scoper for baremetal data model
-------------------------------------
Since baremetal data model was added, we need audit scoper for baremetal
data model as compute data model has.

Enhance watcher Applier engine
------------------------------
Currently watcher's Applier can only run actions one by one or parallel.
We need to decide whether the next action is executed based on the result of
the previous action, so we need to enhance the applier.

.. _admin: https://docs.openstack.org/watcher/pike/glossary.html#administrator
.. _actionplan: https://docs.openstack.org/watcher/pike/glossary.html#action-plan
.. _audit: https://docs.openstack.org/watcher/pike/glossary.html#audit
.. _CDM: https://docs.openstack.org/watcher/pike/glossary.html#cluster-data-model-cdm
.. _planner: https://docs.openstack.org/watcher/pike/glossary.html#watcher-planner
.. _strategy: https://docs.openstack.org/watcher/pike/glossary.html#strategy
.. _actions: https://docs.openstack.org/watcher/pike/glossary.html#action
.. _scope: https://docs.openstack.org/watcher/latest/glossary.html#audit-scope
