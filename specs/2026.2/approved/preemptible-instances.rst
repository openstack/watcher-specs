..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Preemptible Instances
==========================================

https://blueprints.launchpad.net/watcher/+spec/preemptible-instances

This specification introduces the ability to manage preemptible
instances using Watcher. Preemptible instances, often referred to as
spot instances, stem from the idea of enabling cloud providers to
utilize their spare capacity optimally. From the perspective of the
cloud market, this functionality allows paying users to select a
lower-cost alternative if their application is flexible enough.
Additionally, private clouds can leverage this feature for HPC
workloads or AI jobs. Therefore, the key concept is to have a
mechanism to tag instances as "preemptible", and when specific
conditions are met—such as a lack of resources to create on-demand
instances—one or more instances will have their resources released.

Problem description
===================

One of the reasons for the success of the cloud computing model stems
from the capacity to allocate resources elastically. To achieve this,
providers need to be prepared for high demand, as well as for low
demand. This necessity surfaces a challenge when managing cloud
environments: avoid waste of resources when the demand is low,
especially because of the high costs associated with it, both
operational and monetary. At the same time, the actual quota system
only ensures a project to have a fair share of the cloud resources,
but this can also lead to underutilization resources.

A strategy has been already used by hyperscalers: the use of
preemptible instances `[1]`_ `[2]`_. That is, offer instances to use the spare
capacity but they can be interrupted at any time. Currently, OpenStack
does not provide any mechanism to achieve this. We can use Watcher to
have this feature and leverage the decision engine based on data
collected from various exporters to make a better decision about which
instance will be preempted.

Use Cases
----------

* As a public cloud, I can offer users my spare capacity at a steep
  discount rate.

* As a paying user, I can save money by running batch or non critical
  workloads on a VM tier with a minimum time before termination.

* As a university or private HPC cloud I can allow teams to pool their
  hardware to deploy open source, fault-tolerant, and highly scalable
  job scheduling systems like Slurm while still having dedicated
  capacity.

Proposed change
===============

Goal
--------

Since none of the already implemented Watcher's goals look fit on this
feature, we will need a new goal: **Workload Optimization**.

The objective of this goal is to free resources in use by low
priority workloads and therefore optimize capacity for higher priority
workloads. This optimizes infrastructure utilization by allowing lower
priority workloads to use spare capacity while also enabling higher
return on investment when capacity is needed.

Strategy
--------

This spec adds a new strategy called **Workload Preemption**. Its
functionality is described below.

Optimization Target
^^^^^^^^^^^^^^^^^^^^

The goal of optimization is to ensure a certain percentage of free
allocated resources. To achieve this, instances classified as
preemptible will be chosen, and those selected will be preempted to
free up the allocated resources. This approach allows providers to
offer cheaper instances that utilize spare capacity while still
maintaining control over the allocation pool for on-demand instances.

By default, the free resource target is evaluated cluster-wide, i.e.
across all compute nodes managed by Watcher. Operators can narrow this
scope to a subset of the cluster (e.g. a specific host aggregate or
availability zone) by configuring an audit scope on the Audit
Template, without any change to the strategy logic itself.

The operator can configure target free percentage per resource, using
the following parameters:

* ``cpu_free_percentage``
* ``ram_free_percentage``
* ``disk_free_percentage``

These are independent parameters: an operator may choose to enforce a
threshold on a subset of resources only (e.g. only
``cpu_free_percentage``), leaving the others unmonitored. The strategy
evaluates only the resources for which a threshold parameter has been
explicitly set. When more than one resource threshold is configured,
the strategy preempts instances until *all* configured thresholds are
satisfied, which may require freeing more of one resource than another
depending on current allocation pressure.

The optimization objective is also to free exactly enough
**allocated** resources to satisfy the incoming on-demand instance
request while minimizing the number of preemptible instances
terminated. This reduces disruption to preemptible workloads and
preserves as many running preemptible instances as possible.

.. IMPORTANT::
    The thresholds (``cpu_free_percentage``, ``ram_free_percentage``,
    ``disk_free_percentage``) are evaluated against **allocated** resources
    (i.e. vCPU, RAM, or disk reserved by each instance's flavor), not actual
    utilization. This means preemption can be triggered even when real workload
    pressure is low, and conversely may not trigger on a heavily loaded cluster
    if allocations happen to leave enough headroom.

    Note that this applies only to *when* the strategy decides to preempt.
    *Which* instances are selected depends on the ``preemption_preference``
    configuration (see `Generalized Priority Sorting`_): operators can target
    instances with the largest resource allocations first, or sort by age, or
    combine both as tiebreakers.

Candidate Selection and Sorting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The candidate pipeline is split into two distinct, uncoupled stages: a
reusable filtering phase governed by mandatory and conditional invariants,
and a generalized sorting phase driven by operator-defined priority criteria.

Candidate Filtering & Invariants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before any sorting occurs, the strategy utilizes a reusable filtering
function that accepts a list of instances. This function
evaluates every instance against a set of invariants to build the
baseline candidate pool for the affected compute node(s).

* **Mandatory Invariants**: Instances are immediately excluded unless
  they are explicitly annotated as preemptible via their Flavor
  properties

``lifecycle:preemptable=true|false``

* **Conditional Invariants**: The function filters instances based on
  cloud-specific service level agreements (SLAs) or operating
  contracts. A key parameter is ``min_instance_age`` (defaulting to
  3600 seconds). This ensures an instance cannot be preempted
  immediately after creation, protecting the user's workload for
  a guaranteed minimum window. This window can be adjusted by
  operators to reflect their specific cloud context.

Because this filtering logic is encapsulated in a standalone, reusable
function, the strategy can iteratively re-apply the exact same
invariant checks to re-evaluate the cluster data model while computing
and refining the final action plan.

Generalized Priority Sorting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than hardcoding rigid tie-breakers within a single policy,
the strategy implements a generalized algorithm where
sorting criteria are completely decoupled.

The order in which valid candidates are evaluated for termination is
controlled by a ``preemption_preference`` parameter, which accepts a
prioritized list of key-direction tuples. The possible directions are
``asc`` for ascending and ``dec`` for descending direction. Python's
stable sorting behavior is leveraged here via a tuple-projection model
(evaluating criteria sequentially from left to right) to ensure a
deterministic priority chain::

    preemption_preference = [('key1', 'dir1'), ('key2', 'dir2'), ...]

Supported keys include:

* **age**: Evaluated by creation timestamp. Combined with ``dec`` (descending),
  oldest instances are reaped first.

* **resource:<name>**: Evaluated by the instance's Placement
  allocation for the given resource class. ``<name>`` accepts any
  standard resource class defined in ``os-resource-classes`` (e.g.,
  ``VCPU``, ``MEMORY_MB``, ``DISK_GB``, ``VGPU``, ``PCPU``,
  ``SRIOV_NET_VF``) as well as custom resource classes
  (``CUSTOM_*``). Each resource class acts as an independent sort
  key, so operators can control which resource matters most and use
  additional dimensions as tiebreakers. Combined with ``dec``,
  instances with the largest allocation of that specific resource
  class are preempted first, maximizing resellable capacity and
  hitting free-allocation thresholds with the fewest possible
  disruptions. If an instance has no allocation for the specified
  resource class, the value is treated as ``0``.

The default value of ``preemption_preference`` is ``[('age',
'dec')]``, which preempts instances from oldest to newest. This
reflects the common operational expectation that longer-running
preemptible instances have already consumed their fair share of spare
capacity and should be reclaimed first, giving newer instances a
reasonable window to complete their work.

This generalized configuration allows operators to encode their
specific economic intent without requiring separate hardcoded
strategies. For example:

* To prioritize reclaiming instances with the largest vCPU and memory
  footprints first, breaking ties with the oldest instances:
  ``[('resource:vcpu', 'dec'), ('resource:memory_mb', 'asc'), ('age',
  'dec')]``

The strategy iterates over the sorted candidate list, accumulating freed
resources, and stops as soon as the on-demand request can be satisfied.

Efficacy Indicators
^^^^^^^^^^^^^^^^^^^^

The efficacy of a solution is calculated based on the following
criteria:

* **preempted_instances_count**: The total number of preempted
  instances. This is important because it is part of the solution
  release the necessary resources with the fewest instances as
  possible.

* **vcpu_freed**: The total number of vCPUs freed by the solution,
  computed as the sum of the vCPU count of each preempted instance's
  flavor.

* **mem_mb_freed**: The total amount of RAM freed (in MB) by the
  solution, computed as the sum of the RAM size of each preempted
  instance's flavor.

* **disk_gb_freed**: The total amount of disk freed (in GB) by the
  solution, computed as the sum of the root disk size of each
  preempted instance's flavor.

Actions
--------

For the sake of this specification, the strategy can follow two
different policies to preempt an instance. It can be **shelved**,
which keeps all the data and associated resources, but doesn't retain
in-memory information, or it can be **deleted**, in which delete the
instance and all associated resources. The way to perform this on an
instance will be via Watcher's actions and communicating with the Nova
API.

The operator can configure the default preemption policy that will be
used via the input parameter ``preemption_mode``. This parameter has a
default value of ``delete``.

*lifecycle:preempt_policy=shelve|delete*

In order to implement these actions, we need to add two new files:
**delete.py** and **shelve.py** under the **watcher/applier/actions/**
directory.

Their schema is quite simple because we only need to know what is the
instance ID to perform the given action.

.. code-block::

    {
        'resource_id': str  # should be a UUID
    }

Preconditions:
^^^^^^^^^^^^^^^

    Delete:
        * The instance should exist

    Shelve:
        * The instance should exist
        * The instance shouldn't be in *SHELVED* state

Postconditions:
^^^^^^^^^^^^^^^^

    Delete:
        * The instance should no longer exist

    Shelve:
        * The instance should be in *SHELVED* state

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

Operators must set the ``lifecycle:preemptable=true`` property on any
flavor intended to be used for preemptible instances. Flavors without
this property will never be considered candidates for preemption,
regardless of audit configuration.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  winiciusallan

Work Items
----------

* Create two new actions under applier/actions/
* Create a new goal under decision_engine/goal/goals.py
* Create efficacy indicators under decision_engine/goal/efficacy/indicators.py
* Create a new strategy under decision_engine/strategy/strategies/
* Extend the Compute Data Model (CDM) to store each instance's
  resource allocation (``vcpu``, ``memory_mb``, ``disk_gb``)
* Add unit, functional, and integration tempest tests

Dependencies
============

None

Testing
=======

* Unit tests will cover the **PreemptInstances** strategy logic (threshold
  evaluation, candidate filtering/invariants, ``preemption_preference``
  sorting, and efficacy indicators), as well as the ``delete`` and
  ``shelve`` actions and their pre/postconditions.

* New tempest tests will be added for the new strategy which will be
  executed in the existing check/gate CI jobs

Documentation Impact
====================

* Update the strategy matrix.
* A new documentation will be needed for the goal.
* A new documentation will be needed for the strategy.
* Add examples about how to use it in an AuditTemplate and its
  parameters.

References
==========

.. _[1]:

[1] AWS Spot Instances Documentation -
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html

.. _[2]:

[2] GCP Spot VMs - https://cloud.google.com/solutions/spot-vms

[3] Red Hat downstream issue for this feature -
https://redhat.atlassian.net/browse/RHOSRFE-142

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2026.2
     - Introduced
