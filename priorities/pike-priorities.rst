.. _pike-priorities:

=======================
Pike Project Priorities
=======================

List of priorities the Watcher drivers team is prioritizing in Pike.

+-----------------------------------------+-------------------------+
| Priority                                | Owner                   |
+=========================================+=========================+
| `Cinder Model Intergration`_            | `Hidekazu Nakamura`_    |
+-----------------------------------------+-------------------------+
| `Audit tag in VM Metadata`_             | `Prashanth Hari`_       |
+-----------------------------------------+-------------------------+
| `Support Gnocchi in Watcher`_           | `Santhosh Fernandes`_   |
+-----------------------------------------+-------------------------+
| `Noisy Neighbor Strategy`_              | `Prudhvi Rao Shedimbi`_ |
+-----------------------------------------+-------------------------+
| `Workload characterization grammar`_    | `Chris Spencer`_        |
+-----------------------------------------+-------------------------+
| `Stale the Action Plan`_                | `Li Canwei`_            |
+-----------------------------------------+-------------------------+
| `Workload Characterization and QoS`_    | `Susanne Balle`_        |
+-----------------------------------------+-------------------------+
| `Action versioned notifications`_       | `Alexander Chadin`_     |
+-----------------------------------------+-------------------------+
| `Cancel Action Plan`_                   | `aditi sharma`_         |
+-----------------------------------------+-------------------------+
| `Dynamic Action Description`_           | `Charlotte Han`_        |
+-----------------------------------------+-------------------------+
| `Power On and Power Off in Watcher`_    | `Li Canwei`_            |
+-----------------------------------------+-------------------------+
| `Suspended audit state`_                | `Hidekazu Nakamura`_    |
+-----------------------------------------+-------------------------+
| `JSONschema validation`_                | `YumengBao`_            |
+-----------------------------------------+-------------------------+
| `Service versioned notifications`_      | `Vladimir Ostroverkhov`_|
+-----------------------------------------+-------------------------+
| `Notifications for action plan cancel`_ | `aditi sharma`_         |
+-----------------------------------------+-------------------------+
| `Use cron syntax for CONTINUOUS audits`_| `Alexander Chadin`_     |
+-----------------------------------------+-------------------------+
| `Event-driven optimization based`_      | `Alexander Chadin`_     |
+-----------------------------------------+-------------------------+

.. _Hidekazu Nakamura: https://launchpad.net/~nakamura-h
.. _Prashanth Hari: https://launchpad.net/~hvprash
.. _Santhosh Fernandes : https://launchpad.net/~santhosh-fernandes
.. _Prudhvi Rao Shedimbi: https://launchpad.net/~prudhvi-rao-shedimbi
.. _Chris Spencer: https://launchpad.net/~christopher-m-spencer
.. _Susanne Balle: https://launchpad.net/~susanne-balle
.. _Charlotte Han: https://launchpad.net/~hanrong
.. _Alexander Chadin: https://launchpad.net/~joker946
.. _aditi sharma: https://launchpad.net/~adi-sky17
.. _Li Canwei: https://launchpad.net/~li-canwei2
.. _YumengBao: https://launchpad.net/~yumeng-bao
.. _Vladimir Ostroverkhov: https://launchpad.net/~ostroverkhov-6


Cinder Model Intergration
-------------------------

Extend Watcher `Cluster Data Model`_ with Cinder-related data.
There should be able following features:
To integrate storage info at the model build stage

To consume all the needed Cinder Notifications in order to maintain
the consistency of the storage-related part of the model

To easily query/retrieve the storage information from within a strategy
via a clear set of methods

Audit tag in VM Metadata
------------------------

When Watcher runs `Audit`_ to achieve a `Goal`_, there should be some way for
the application/VM owners to know that their VMs are under audit and is
flagged for `Action Plan`_ execution. These information could be stored in VM
metadata with a timestamp after which action plan will be executed.

Support Gnocchi in Watcher
--------------------------
Today, Watcher uses Telemetry and Monasca to collect metrics from the
`Cluster`_. There is need to support `Gnocchi`_ as well since Ceilometer v2 API
is deprecated.

Noisy Neighbor Strategy
-----------------------

L3 cache is critical and limit system level resource shared by all apps or
VMs on one node. If one VM occupies most of L3 cache, other VMs on the node
likely starve without enough L3 cache thus poor performance.

This BP adds a new `Strategy`_ to detect then migrate such cache greedy VM
based on some new cache/memory metrics.

Workload characterization grammar
---------------------------------

As we run several workloads in cloud, we should be able to characterize such
workloads as input to watcher for ensuring Application QoS, placements and
consolidation.

An example of workload characterization is a weighted combination of CPU,
Memory or any other resource attributes like High IOPs, Network latency etc.

Scope of this blueprint is to come up with a grammar structure for defining
workload character.

Stale the Action Plan
---------------------

When an audit is created and launched successfully, it generates a new Action
Plan with status RECOMMENDED. If the Cluster Data Model has changed by and by,
the action plan is still keep the RECOMMENDED state. There is not an expiry
date or event that can invalidate the action plan by far.

Workload Characterization and QoS
---------------------------------

Based on the defined workload characteristics we should be able to apply
Quality of Services to applications. An example would be leveraging
technologies like Intel RDT.

This opens up several application optimization possibilities
(use cases like NFV etc.) and also ensures efficient use of cloud resources.
Scope of this blueprint is to build a QoS strategy using Intel RDT and workload
grammar.

Action versioned notifications
------------------------------

As of now, there is no way for any service (Watcher included) to know when an
action has been created, modified or deleted. This prevents any form of
event-based reaction which may be useful for 3rd party services or plugins.

This blueprint should define the list of Action notifications to be implemented
as well as their respective payload structures.

Cancel Action Plan
------------------

As of now Administrator can update the action plan state to **CANCELLED** but
there is no action taken by Watcher to cancel the action plan. It only updates
the action plan state to **CANCELLED**.

It should be possible to **CANCEL** execution of the action plan by Watcher.

Dynamic Action Description
--------------------------

By introducing a new way, for developer, to implement a strategy with new
customized actions (blueprint watcher-add-actions-via-conf),
we have no more the possibility to have the literal description of an planned
`Action`_ before to execute it (in the `Watcher Applier`_). This literal
description is important when the cloud admin want to see details information
about a recommended action plan.

Power On and Power Off in Watcher
---------------------------------

Watcher need one strategy which can reduce the power consumption.

A traffic system could be running on many virtual machines. The traffic is busy
during day time, so the traffic system would increase virtual machines' number
to satisfy its workload. But during the night, the traffic's workload decreases
obviously, so this traffic system would delete redundant virtual machines.
This feature we call "elastic scaling" in telecom.

The telecom operators have their own hardware equipment and sometimes the size
of hardware is large. So telecom operators want to use cloud center manager
software to reduce the energy consumption of hardware automatically based on
"elastic scaling".

Suspended audit state
---------------------

As of now Watcher have to delete audit and recreate audit if administrator
want to stop creating action plan of audit with continuous mode.

This blueprint adds suspended audit state for stopping creation of action plan
related to audit with continuous mode.

JSONschema validation
---------------------

As of now in Watcher both jsonschema and voluptuous are used to validate
JSON payloads. However, the problem with voluptuous is that its structure is
not standardized compare to jsonschema which means that we cannot easily
expose the validation schema through our API.

Service versioned notifications
-------------------------------

As of now, there is no way for any service (Watcher included) to know when an
action has been created, modified or deleted. This prevents any form of
event-based reaction which may be useful for 3rd party services or plugins.

This blueprint should define the list of Service notifications to be
implemented as well as their respective payload structures.

Notifications for action plan cancel
------------------------------------

Notifications needs to be added to action and actionplan for new operation
actionplan cancel.

Use cron syntax for CONTINUOUS audits
-------------------------------------

As of now we use a period in seconds to schedule continuous audits.
This works well but does not really give the flexibility that an operator
might actually want. Therefore, we should also provide a way to express out
scheduling needs via the cron syntax which shall give operators a fine grained
control.

This change implies the refactoring of the API so backward compatibility should
be guaranteed.
On the Watcher dashboard side, we should also provide an easy-to-use form to
fill in this cron field.

We should also keep the cron syntax and the creation timestamp in the DB

Event-driven optimization based
-------------------------------

We propose an event-driven optimization-based audit control.
We wants to select among a list of events which may trigger the audit :

- React to a predicted situation.

- React to a critical situations and changes in system (e.g: threshold )

- A new compute node has been added to the cluster

- A compute node has been removed from the cluster

- A new virtual machine has been created

.. _Cluster: http://docs.openstack.org/developer/watcher/glossary.html#cluster-definition
.. _Cluster Data Model: https://docs.openstack.org/developer/watcher/glossary.html#cluster-data-model-cdm
.. _Gnocchi: https://wiki.openstack.org/wiki/Gnocchi
.. _Host Aggregates: http://docs.openstack.org/developer/nova/aggregates.html
.. _Availability Zones: http://docs.openstack.org/developer/nova/aggregates.html#availability-zones-azs
.. _oslo.versionnedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/
.. _Action Plan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan-definition
.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit-definition
.. _Action: http://docs.openstack.org/developer/watcher/glossary.html#action-definition
.. _Strategy: http://docs.openstack.org/developer/watcher/glossary.html#strategy-definition
.. _Nova Notifications: http://docs.openstack.org/developer/nova/notifications.html
.. _Goal: http://docs.openstack.org/developer/watcher/glossary.html#goal
.. _Watcher Applier: https://docs.openstack.org/developer/watcher/glossary.html#watcher-applier
