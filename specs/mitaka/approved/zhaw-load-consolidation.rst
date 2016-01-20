..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===========================
Load consolidation strategy
===========================

This specification relates to blueprint:
https://blueprints.launchpad.net/watcher/+spec/basic-cloud-consolidation-integration

Problem description
===================

Watcher is a framework which provides support for more energy efficient
OpenStack operations. It does this by providing access to system state
information and a set of available actions which can be performed on an
OpenStack installation. It is specifically designed to provide support for
different approaches to realizing energy efficient operations: consequently,
interested parties are encouraged to provide their own energy efficiency
approaches and integrate them with Watcher. This specification focuses on
integration of the rudimentary load consolidation mechanism developed at
ICCLab cloud computing research lab at Zürcher Hochschule für Angewandte
Wissenschaften (ZHAW) with Watcher.

The original code implementing this algorithm (not in the context of Watcher)
was published here:
https://github.com/icclab/cloud-consolidation

Use Cases
---------

The use case is one in which the `Administrator`_ wants to perform a load
consolidation on the `resources`_ to reduce the amount of underutilized
servers. The Administrator invokes Watcher with the `Goal`_ of
“VM_WORKLOAD_CONSOLIDATION”. Watcher then executes the `Strategy`_
“VM_WORKLOAD_CONSOLIDATION_STRATEGY”. It then presents a set of `Actions`_
to the  Administrator. The Administrator then approves the recommended
`action plan`_ - typically VM live-migration actions - and instructs Watcher
to perform the actions.

Project Priority
----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

The proposed change is to add a new Goal and a new Strategy to Watcher.
The new Goal is “VM_WORKLOAD_CONSOLIDATION” and the new Strategy is
“VM_WORKLOAD_CONSOLIDATION_STRATEGY”. The new Strategy is designed to be a
lightweight consolidation mechanism which can be tuned based on experience; it
also operates quickly. The purpose of the strategy is to move the aggregate
operating point of the `Cluster`_ to increase the number of servers with
moderate to high load and minimize the number of servers with low load.
This can be used in conjunction with a server management mechanism to reduce
overall energy consumption.

The new Strategy will leverage a modified first-fit algorithm to achieve
increased server CPU and memory utilization which ultimately leads to freeing
some of the hosts that can be powered down to save energy. It comprises of
two phases, one focused on identifying server with high load and reducing their
load and one focused on identifying servers which have spare underutilized
capacity. Each of these operates as a first-fit algorithm with utilization
ordered in different ways as input to each.

This Strategy will consider compute host's CPU utilization and memory
constraints. These upper utilization thresholds can be set relative to resource
capacity and hence will provide simple resource overbooking management if
needed. This strategy will not deal with any other limitations such as actual
VM memory change rate, network constraints, etc. and relies upon a robust live
migration mechanism.

In order to be able to predict host resources utilization the following
utilization estimation model is used. A host resource utilization equals to a
sum of the resource utilizations of the hosted workloads (VMs). Considering
hosts H1, H2 with a workload W running on H1, moving the workload W from H1 to
H2 will result in predicted resource utilization as follows: H1 = H1 - W and
H2 = H2 + W with the metrics relating to the VM taken from telemetry and those
pertaining to the host available via nova metrics.

The strategy will work in two phases.
The first phase handles decreasingly sorted hosts (by their CPU utilization)
whose CPU utilization is exceeding defined threshold and offloads their
workload (VM) to the first suitable less loaded host which is able to
accommodate the workload without violating any of the constraints described.
This host offloading process is repeated for all overloaded hosts until the
host’s CPU utilization is predicted to be under the threshold. Doing so for
all overloaded servers outputs in a system without overloaded servers. In
this phase the workloads (VM) are handled sorted increasingly by its CPU
utilization.
The second phase then iterates through the servers in reversed order (sorted
increasingly by their CPU utilization and thus starting with the least
loaded servers) and looks for a smallest possible space where to accommodate
its remaining workloads starting with the largest workload and the most loaded
hosts. This process is repeated until there is no workload (VM) left on the
host in which case this host can be deactivated. This continues again for the
next hosts in the same manner until the source and the destination host
becomes the same. In this phase the workloads (VM) are handled sorted
decreasingly by its CPU utilization.

Both phases result in a solution whose execution leads to a consolidated system
with no overloaded hosts.

This change will not affect any existing Strategies and will not affect Watcher
performance.

Concretely, the new Strategy will be implemented as a new Strategy called
VMWorkloadConsolidationStrategy inheriting from BaseStrategy. The
implementation will be very much based on the BasicConsolidation example in the
current Watcher codebase.

Alternatives
------------

The alternatives to this approach are to use different Goals and associated
Strategies defined in Watcher.

Data model impact
-----------------

None expected.

Having reviewed the data models for both information available to the different
Strategies as well as the data models for the Actions, we believe that no
modifications are necessary to implement this Strategy.

REST API impact
---------------

There is no impact on the REST API.

Security impact
---------------

As the strategy only computes a new VM placement and doesn’t deal with
placement itself, no security impact is envisaged.

Notifications impact
--------------------

No specific notifications associated with executing a specific Strategy are
envisaged. (Notifications could arise from the resulting actions, but these
are presumably handled in other parts of Watcher).

Other end user impact
---------------------

This capability will not have any specific impact on the API. It will have a
small impact in how it is used via the python-watcherclient as a new option
will now be available for goal parameter in an Audit Template.

Performance Impact
------------------

No specific performance impact is envisaged. The Strategy has been designed
to operate over hundreds of servers in the order of a few seconds.

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
  Seán Murphy <murp>
Other contributors:
  Bruno Grazioli <bwg-bruno>
  Vojtech Cima <cima-vojtech>

Work Items
----------

This task can be considered atomic. It just requires the development and
test of a single class.

Dependencies
============

No dependencies.

Testing
=======

Several unit tests will be provided to test various scenarios using a fake
mock models (mock model collector and mock metrics collector) including edge
scenarios such as a consolidation of an empty cluster, a consolidation of
randomly generated clusters or consolidation of an overloaded cluster.

Testing approaches similar to the basic consolidation strategy will be
used, comprising of unit tests and integration tests in which a specific
input is given and compared against the expected output.

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
.. _resources: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#managed-resource
.. _Goal: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#goal
.. _Strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Actions: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action
.. _action plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Cluster: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#cluster
