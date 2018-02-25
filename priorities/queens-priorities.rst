.. _queens-priorities:

=========================
Queens Project Priorities
=========================

List of priorities the Watcher drivers team is prioritizing in Queens.

+------------------------------------------+----------------------+
| Priority                                 | Owner                |
+==========================================+======================+
| `Baremetal data model in Watcher`_       | `Li Canwei`_         |
+------------------------------------------+----------------------+
| `Check the strategy requirements`_       | `Alexander Chadin`_  |
+------------------------------------------+----------------------+
| `Notifications for action plan cancel`_  | `Aditi Sharma`_      |
+------------------------------------------+----------------------+
| `Watcher Planner Selector`_              | `Alexander Chadin`_  |
+------------------------------------------+----------------------+
| `Watcher Strategy Selector`_             | `Aditi Sharma`_      |
+------------------------------------------+----------------------+
| `Workload Characterization and QoS`_     | `Susanne Balle`_     |
+------------------------------------------+----------------------+
| `Extend node status`_                    | `suzhengwei`_        |
+------------------------------------------+----------------------+
| `Exclude project by audit scope`_        | `Aditi Sharma`_      |
+------------------------------------------+----------------------+
| `Audit scoper for storage data model`_   | `Hidekazu Nakamura`_ |
+------------------------------------------+----------------------+
| `Define a tailored Scoper for each CDM`_ | `Hidekazu Nakamura`_ |
+------------------------------------------+----------------------+
| `Register and Document Policy in Code`_  | `Yumeng Bao`_        |
+------------------------------------------+----------------------+
| `Workload characterization grammar`_     | `Susanne Balle`_     |
+------------------------------------------+----------------------+
| `Zone migration strategy`_               | `Hidekazu Nakamura`_ |
+------------------------------------------+----------------------+
| `Watcher API validation using JSON`_     | `Aditi Sharma`_      |
+------------------------------------------+----------------------+
| `Compute CDM include all instances`_     | `suzhengwei`_        |
+------------------------------------------+----------------------+
| `Display input parameters of strategy`_  | `Alexander Chadin`_  |
+------------------------------------------+----------------------+
| `Add name for audit`_                    | `suzhengwei`_        |
+------------------------------------------+----------------------+
| `Cluster maintance strategy`_            | `suzhengwei`_        |
+------------------------------------------+----------------------+
| `Multiple datasources for strategies`_   | `Aditi Sharma`_      |
+------------------------------------------+----------------------+
| `Replace voplutuous with JSON Schema`_   | `Yumeng Bao`_        |
+------------------------------------------+----------------------+

.. _Charlotte Han: https://launchpad.net/~hanrong
.. _Hidekazu Nakamura: https://launchpad.net/~nakamura-h
.. _Alexander Chadin: https://launchpad.net/~joker946
.. _Kevin Mullery: https://launchpad.net/~kmullery
.. _Li Canwei: https://launchpad.net/~li-canwei2
.. _Yumeng Bao: https://launchpad.net/~yumeng-bao
.. _Aditi Sharma: https://launchpad.net/~adi-sky17
.. _suzhengwei: https://launchpad.net/~sue.sam
.. _Susanne Balle: https://launchpad.net/~susanne-balle


Baremetal data model in Watcher
-------------------------------

For a data center with large amount of VMs and physical hosts,the total power
consumption is tremendous. When workload is not heavy, Watcher can be used to
reduce power consumption by triggering a request to power off some idle hosts
without VMs. And when the workload increases Watcher will trigger a "power on"
request to fulfill the service requirements.

Check the strategy requirements
-------------------------------

Running of `strategy`_ requires different type of data resources to compute a
`solution`_. During the strategies loading, the `decision engine`_ should
automatically check if all requirements are achieved.

Notifications for action plan cancel
------------------------------------

Notifications needs to be added to `action`_ and `action plan`_ for new
operation action plan cancel.

Watcher Planner Selector
------------------------

This component is responsible for selecting an appropriate `planner`_ for a
given strategy depending on several factors (e.g list of actions used by the
strategy or user request).


Watcher Strategy Selector
-------------------------
There may be several strategies applying for a given optimization `goal`_.
Currently , if the admin didn't specify a strategy Watcher select the first
strategy available in the list. If Watcher intends to be used in real
infrastructure it need a more robust way to select the strategy for a given
goal. The strategy selector component will enable watcher to automatically
decide which strategy to use.

Workload Characterization and QoS
---------------------------------

Based on the defined workload characteristics we should be able to apply
Quality of Services to applications. An example would be leveraging
technologies like Intel RDT.

This opens up several application optimization possibilities
(use cases like NFV etc.) and also ensures efficient use of cloud resources.
Scope of this blueprint is to build a QoS strategy using Intel RDT and workload
grammar.

Extend node status
------------------

We can get a node status through `CDM`_ (cluster data model) in watcher. Most
of strategies rely on the node's status. But the existing status just meets
existing strategies. We need to extend nodes status description for new
strategies.

Exclude project by audit scope
------------------------------

As of Now, Watcher can exclude instances, compute_nodes, host_aggregates and
instance_metadata by audit scope. As an administrator, I want to exclude
instances of a specific project from Watcher optimization. This bp proposes to
add exclude project feature to audit scope.

Audit scoper for storage data model
-----------------------------------

Since storage data model was added in Pike cycle, we need audit scoper for
storage data model as compute data model has.

Define a tailored Scoper for each CDM
-------------------------------------

Storage cluster data model was introduced in Pike cycle. Since the model is
different from compute data model, current single CDM scoper does not work
for the model.

Register and Document Policy in Code
------------------------------------

This blueprint tracks the work for moving default policies and documentation
into code. This is OpenStack-wide goals for Queens release.
https://governance.openstack.org/tc/goals/queens/policy-in-code.html

Storage workload balance
------------------------

As of now, Watcher optimizes only compute nodes.
Storage optimization is also important feature for centralized storage
(non distributed storage). This spec will add Storage Workload Balance
Strategy to balance the storage resource. And we can use existing goal
(workload_balancing) and action(volume_migrate) for storage workload balance.

Workload characterization grammar
---------------------------------

As we run several workloads in cloud, we should be able to characterize such
workloads as input to watcher for ensuring Application QoS, placements and
consolidation.

An example of workload characterization is a weighted combination of CPU,
Memory or any other resource attributes like High IOPs, Network latency etc.

Scope of this blueprint is to come up with a grammar structure for defining
workload character.

Zone migration strategy
-----------------------

There are thousands of physical servers and storage running various kinds of
workloads in the Cloud system. Administrator have to migrate instances and
block storage for hardware maintenance once a quarter or so. It requires
operators manually to watch workloads, choose instances to migrate and migrate
for each instances and block storage for efficiently, with minimum downtime.
Watcher can be used to do this task automatically.

Watcher API validation using JSON
---------------------------------

Cureently watcher uses different methods to validate api, which causes many
bugs and few operations are possible which should not be allowed like a cloud
admin can delete "ongoing" actionplan and audit. To have more cleaner and same
approach for all operations we should have a unified way of validating the api,
which can be done using JSON.

Compute CDM include all instances
---------------------------------

When building compute CDM, Watcher excludes the instances excluded in the
scope. It has negative impact to Watcher.

* To some strategies, it get incorrectly workload of the compute nodes,
  because the excluded instances was not calculated in.
* To server consolidation, it disables the nodes which has excluded instances
  running.

Display input parameters of strategy
------------------------------------

As of now in watcher, it is difficult for users to know what input-parameters
are required by each strategy when creating an audit. This blueprint will add
a column to display input parameters of each strategy in results of
"watcher strategy list".

Add name for audit
------------------

Adding name for audit entity would be more friendly to end users to interact
with audit. This blueprint suggests to add name property to audit entity,
so it will be easy for users to retrieve an andit by name.

Cluster maintance strategy
--------------------------

Sometimes we need to maintain compute nodes, update hardware and software,
and so on. But we don't want user's application to be interrupted. This issue
imports one goal and strategy for manually maintaining without user's
application interruption.

Multiple datasources for strategies
-----------------------------------

We need an abstraction layer with a minimal subset of metrics needed by
existing strategies (it will deal with gnocchi & monasca). If we have multiple
metrics collection backend deployed, the strategy will need to give the
back-end it wants to use / alternatively we could define a backend priority in
configuration. We will need a map between metrics names used by strategies and
correspond names in backends.

Multiple global efficacy indicator
----------------------------------

As of now global `efficacy indicator`_ is a single entity. It is useful for the
strategies which optimizes only one resource like server consolidation works
only with instances. There can be some future strategies which optimizes many
resources (volume, instance, network) for them it is necessary to calculate
global efficacy for each resource. This blueprint will implement multiple
global efficacy indicator.

Replace voplutuous with JSON Schema
-----------------------------------

In this blueprint, we will replace voplutuous with JSON-schema to validate
efficacy indicator. Since we want to remove voluptuous and use
JSONSchema as our only JSON validation tool to keep consistency in Watcher.

.. _strategy: https://docs.openstack.org/watcher/latest/glossary.html#strategy
.. _solution: https://docs.openstack.org/watcher/latest/glossary.html#solution
.. _decision engine: https://docs.openstack.org/watcher/latest/glossary.html#watcher-decision-engine
.. _action: https://docs.openstack.org/watcher/latest/glossary.html#action
.. _action plan: https://docs.openstack.org/watcher/latest/glossary.html#action-plan
.. _CDM: https://docs.openstack.org/watcher/latest/glossary.html#cluster-data-model-cdm
.. _goal: https://docs.openstack.org/watcher/latest/glossary.html#goal
.. _planner: https://docs.openstack.org/watcher/latest/glossary.html#watcher-planner
.. _efficacy indicator: https://docs.openstack.org/watcher/latest/glossary.html#efficacy-indicator
