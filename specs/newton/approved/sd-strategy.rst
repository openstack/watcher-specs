=============================================
Watcher Overload standard deviation algorithm
=============================================

https://blueprints.launchpad.net/watcher/+spec/watcher-overload-sd


Problem description
===================

Cluster overload is a complex problem, that can be solved by migrating VMs
from one node to another. The decision to migrate is based on VM parameters
such as CPU utilization or memory utilization. We propose a strategy
for Watcher, that monitors if there is a higher load on some hosts compared
to other hosts in the cluster and re-balances the work across hosts
to minimize the standard deviation of the loads in a cluster.

The main purpose of the strategy is to choose the pair VM:dest_host that
minimizes the standard deviation in a cluster best.

This specification relates to blueprint:
https://blueprints.launchpad.net/watcher/+spec/watcher-overload-sd

The original code implementing this algorithm (not in the context of Watcher)
was published here:
https://github.com/joker946/nova/commits/drs

Use Cases
---------

As the `Administrator`_ I want to reduce load on `cluster`_ by triggering
a Watcher optimization with the Workload Stabilization `goal`_ to create
`action plan`_ with the list of recommended actions. This strategy can be
configured by using `watcher input parameters`_ (e.g. thresholds, weights,
metrics). After then I approve proposed action plan, which contains set of VM
live-migration actions.

Project Priority
----------------

Not relevant because Watcher is not in the big tent so far.


Proposed change
===============

The new Workload Stabilization Strategy allows to determine if there is
an outlier in the load for the hosts in a cluster and respond to it
by migrating VMs to average the load across the cluster.
Input: It is possible to get information about workload of every VM
using Ceilometer. In order to do that the means of CPU and RAM utilization
for the last 10 minutes are used (configurable). Then the hypervisor workload
of each node can be calculated by summing up workload of all VMs on each node.
Knowing total amount of CPU and RAM on every node allows
to normalise CPU and RAM load. After that the means of CPU and RAM loads
for the cluster are calculated. All this information makes it possible
to calculate the standard deviation of CPU or RAM. After standard deviation is
calclulated for CPU and RAM, the strategy compares sd values to cpu_threshold
and ram_threshold (these are provided by watcher input parameters).
If one of the values is greater than the threshold value, the strategy runs
cluster stabilization process to reduce load on cluster by performing
live-migration of VMs.
Pseudo code::

    load_for_node = {'compute1': {'cpu', 'ram'}, 'compute2': ...}
    for all vm in node:
        load_for_vm = {'uuid', 'cpu_util', 'memory.resident', 'vcpus'}
        load_for_vm[cpu_util] = transform_vm_cpu_util_to_host_cpu_util()
        load_for_node += load_for_vm
    load_for_cluster = normalize load_for_node

    for all node in cluster:
        compute deviation for each node against load_for_cluster.
        Then choose the src vm and dest host.

The implementation of transform_vm_cpu_util_to_host_cpu_util function is
described in a Cluster stabilization process paragraph.

Cluster stabilization process:
For each active VM we simulate migration to another node of the cluster
by recalculating workload of source node and destination node. The following
code shows a general case of simulating::

    new_hosts[src_hp_id][metric] -= vm_load[metric]
    new_hosts[dst_hp_id][metric] += vm_load[metric]

Meanwhile, the shown code isn't acceptable for cpu_util metric because of
probable difference in the number of node vcpus. Therefore we transform
VM CPU utilization to overall host CPU utilization. The following pseudocode
shows the right way of transforming:

:math:`cpu_impact = cpu_util * vm_vcpus/host_vcpus`

After that the load values of nodes are normalised and the new
standard deviation is calculated with them.
The total standard deviation is calculated as weighted arithmetic mean:

:math:`\sum weight_metric*sd_metric`, where:

* weight_metric is the weight of metric. The value of weight is to be in
  range(0, 1). Each weight of metric is set by `watcher input parameters`_.
* sd_metric is a calculated standard deviation of metric in cluster.

From all options of moving VM to other nodes we choose the one that minimizes
the standard deviation in a cluster best. That option is added
to the map of migration options, that afterwards gets sorted
by standard deviation in ascending order. From the resulting list
we iteratively take a host/vm pair and place it into solution with
action “MIGRATION”. We compare the resulting deviations of CPU and RAM
to the threshold values. If the resulting deviations are less than
the threshold values, the cycle stops and the resulting action plan
is sent to Watcher Applier.

Alternatives
------------

The alternatives to this approach are to use different Goals and associated
Strategies defined in Watcher.

Data model impact
-----------------

None expected.

REST API impact
---------------

There is no impact on the REST API.

Security impact
---------------

None expected.

Notifications impact
--------------------

No specific notifications associated with executing a specific Strategy are
envisaged. (Notifications could arise from the resulting actions, but these
are presumably handled in other parts of Watcher).

Other end user impact
---------------------

This capability will not have any specific impact
on either the API or python-watcherclient.

Performance Impact
------------------

No specific performance impact is expected.

Other deployer impact
---------------------

No specific deployer impact is envisaged.

Developer impact
----------------

This will not impact other developers working on OpenStack.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Alexander Chadin <alexchadin>
Other contributors:
  Alexander Stavitskiy <alexstav>

Work Items
----------

This task can be considered atomic. It just requires the development and
test of a single class. The main WorkloadStabilization class of this strategy
is inherited from BaseStrategy class.

Dependencies
============

There is a dependency with BP `optimization threshold`_.

Testing
=======

Several unit tests will be provided to test various scenarios.

Documentation Impact
====================

It will be necessary to add new content relating to this new Goal and Strategy
to the documentation.

References
==========

No references.

History
=======

No history.


.. _Administrator: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#administrator
.. _goal: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#goal
.. _action plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _watcher input parameters: https://blueprints.launchpad.net/watcher/+spec/optimization-threshold
.. _cluster: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#cluster
.. _optimization threshold: https://blueprints.launchpad.net/openstack/?searchtext=optimization-threshold