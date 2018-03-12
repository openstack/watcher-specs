.. rocky-priorities:

========================
Rocky Project Priorities
========================

List of priorities the Watcher drivers team is prioritizing in Rocky.

+-------------------------------------------------+-----------------------+
| Priority                                        | Owner                 |
+=================================================+=======================+
| `Watcher API validation using JSON`_            | `Aditi Sharma`_       |
+-------------------------------------------------+-----------------------+
| `Migrate to Zuulv3`_                            | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Compute CDM include all instances`_            | `suzhengwei`_         |
+-------------------------------------------------+-----------------------+
| `Watcher Planner Selector`_                     | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Watcher Strategy Selector`_                    | `Aditi Sharma`_       |
+-------------------------------------------------+-----------------------+
| `Exclude project by audit scope`_               | `Aditi Sharma`_       |
+-------------------------------------------------+-----------------------+
| `Define grammar for workload characterization`_ | `Alexander Chadin`_   |
+-------------------------------------------------+-----------------------+
| `Replace cold migration to use Nova API`_       | `Hidekazu Nakamura`_  |
+-------------------------------------------------+-----------------------+
| `JSONschema to validate efficacy indicators`_   | `Yumeng Bao`_         |
+-------------------------------------------------+-----------------------+
| `Support Watcher HA active-active mode`_        | `Li Canwei`_          |
+-------------------------------------------------+-----------------------+
| `Ironic notifications for bare metal DM`_       | `Yumeng Bao`_         |
+-------------------------------------------------+-----------------------+
| `Cluster maintenance`_                          | `suzhengwei`_         |
+-------------------------------------------------+-----------------------+
| `Add name for audit in watcher dashboard`_      | `Yumeng Bao`_         |
+-------------------------------------------------+-----------------------+
| `Add the start/end time for CONTINUOUS audit`_  | `Li Canwei`_          |
+-------------------------------------------------+-----------------------+
| `Audit scoper for baremetal data model`_        | `Yumeng Bao`_         |
+-------------------------------------------------+-----------------------+
| `Enhance watcher Applier engine`_               | `Li Canwei`_          |
+-------------------------------------------------+-----------------------+


.. _Hidekazu Nakamura: https://launchpad.net/~nakamura-h
.. _Alexander Chadin: https://launchpad.net/~joker946
.. _Li Canwei: https://launchpad.net/~li-canwei2
.. _Yumeng Bao: https://launchpad.net/~yumeng-bao
.. _Aditi Sharma: https://launchpad.net/~adi-sky17
.. _suzhengwei: https://launchpad.net/~sue.sam


Watcher API validation using JSON
---------------------------------
Cureently Watcher uses different methods to validate API, which causes many
bugs and few operations are possible which should not be allowed like a cloud
`admin`_ can delete "ongoing" `actionplan`_ and `audit`_. To have more cleaner
and same approach for all operations we should have a unified way of
validating the API, which can be done using JSON.

Migrate to Zuulv3
-----------------
For all of the jobs specific to a particular project, teams should move the
auto-converted legacy- jobs to their own repos and rework them to stop using
the legacy interfaces. There are two fundamental steps:

1. Move the jobs to your repo
2. Rework the jobs to be native v3 jobs

Compute CDM include all instances
---------------------------------
When building compute `CDM`_, we will exclude the instances excluded in the
scope. It has terrible impact to Watcher.

* To some strategies, it would get incorrectly workload of the compute nodes,
  because the excluded instances was not calculated in.

* To server consolidation, it would disable the nodes which has excluded
  instances running.

Proposal is to include all instances in the scope when build compute CDM.
But exclude the instances excluded in the scope when migrations or simulate
migrations.

Watcher Planner Selector
------------------------
This component is responsible for selecting an appropriate `planner`_ for a
given `strategy`_ depending on several factors (e.g list of `actions`_ used by
the strategy or user request)

Watcher Strategy Selector
-------------------------
There may be several strategies applying for a given optimization goal.
Currently , if the admin didn't specify a strategy watcher select the first
strategy available in the list. If Watcher intends to be used in real
infrastructure it need a more robust way to select the strategy for a given
goal. The strategy selector component will enable watcher to automatically
decide which strategy to use.
The typical use case for this blueprint is :

1) The admin selects a goal from the set of available goals.

2) The strategy selector select the strategy which maximize the strategy
   "objective function" depending on several factors.

3) Once a strategy has been selected, it triggers the Watcher Optimizer
   (DefaultStrategyContext) with it.

Exclude project by audit scope
------------------------------
As an administrator, I want to exclude instances of a specific project from
Watcher optimization.
This bp proposes to add exclude project feature to audit `scope`_.
We need the following tasks:

* Add tenant_id to Compute CDM

* Add exclude project logic in audit scope

Define grammar for workload characterization
--------------------------------------------
As we run several workloads in a cloud, we should be able to characterize
such workloads as input to watcher for ensuring Application QoS, placements
and consolidation. An example of workload characterization is a weighted
combination of CPU, Memory or any other resource attributes like High IOPs,
Network latency etc.

Replace cold migration to use Nova API
--------------------------------------
As of Now Watcher implements cold migrate in migrate action by not using Nova
migration API, since Nova migration API for cold migration could not specify
target host. In Queens cycle, Nova has implemented to specify target host for
cold migration.

JSONschema to validate efficacy indicators
------------------------------------------
In this blueprint, we will replace voplutuous with JSON-schema to validate
efficacy indicator. Since in watcher we want to remove voluptuous and use
JSONSchema as our only JSON validation tool to keep consistency.

Support Watcher HA active-active mode
-------------------------------------
Only one Decision engine can consume notification from nova and we need
to get DEs synced. It can be solved by invoking method on all DEs hosts.

Ironic notifications for bare metal DM
--------------------------------------
Update the bare metal data model by ironic notifications

Cluster maintenance
-------------------
Sometimes we need to maintain compute nodes, update hardware and software,
and so on. But we don't want user's application to be interrupted. This issue
imports one goal and strategy for manually maintaining without user's
application interruption.

Add name for audit in watcher dashboard
---------------------------------------
It is not easy to tell the audits apart just by uuid for end users. If we add
a name for an audit, it is more friendly to end users.
This bp implements adding name for an audit in watcher dashboard.

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
