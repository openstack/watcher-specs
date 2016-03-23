..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================
Select destinations filter
==========================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/select-destinations-filter

Watcher aims at providing an open solution for auditing any pool of resources
and optimizing it through recommended `Actions`_.

This blueprint aims at dealing with the ability to find the best possible
target host in case of a live migration as a Watcher action. Today the action
of filtering hosts is done inside the `strategy`_ but should be done as a
common function for all our strategies.

This work will allow a code factorization and an easier maintenance if the Nova
method `select_destinations(self, context, spec_obj)` evolves.

Problem description
===================

Today the filtering of targeted hosts in case of a migration of VMs is done in
the strategy but this function should be available as a standalone function in
Watcher to allow any strategy developper to rely on only one filtering
function.
This function will be maintained by the Watcher team and deeply related to the
`select_destinations(self, context, spec_obj)` method in Nova.

Use Cases
----------

This is a pure refactoring effort for cleaning up all the code and move it from
the basic consolidation strategy to a generic
`select_destinations(self, hypervisors)` method.

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

Move the code of the method `check_migration(self, model, src_hypervisor,
dest_hypervisor, vm_to_mig))` in
`watcher/decision_engine/strategy/strategies/basic_consolidation.py` outside of
the strategy implementation to be able to use it from any strategy available in
Watcher.

Rename this method as `select_destinations(self, hypervisors)` and update it
to handle a list of possible compute nodes as input that will be filtered
according to the available capacity of each compute node.

Provide a convenient way to add new implementations of
`select_destinations(self, hypervisors)`.

Alternatives
------------

One alternative is to call directly the Nova
`select_destinations(self, context, spec_obj)` method via RPC but after
discussions with the Nova team over IRC [1], it is not a viable solution due to
performance issues on Nova side.

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

Strategy developers will have to rely on this new method to handle the
filtering of targeted hosts in case of migration as an action.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <launchpad-id or None>

Other contributors:
  <launchpad-id or None>

Work Items
----------

*  Move the code of the method `score_of_nodes(self, current_model, score)` in
   `watcher/decision_engine/strategy/strategies/basic_consolidation.py` outside
   the strategy implementation to be able to use it from any strategy
   available in Watcher.

* Rename the method as `select_destinations(self, hypervisors)`.

* Provide a stevedore extension to load dynamically the implementation of
  `select_destinations(self, hypervisors)`.

* Refactor existing strategies to use `select_destinations(self, hypervisors)`
  method.

* Make it available to every strategy developer.

Dependencies
============

None

Testing
=======

* Existing unit tests should continue to pass after moving the method outside
  of the basic consolidation strategy.

* We should also load the `select_destinations(self, hypervisors)` from another
  strategy and verify that hosts filtering is still good.

* Unit tests are needed for dynamic loading of
  `select_destinations(self, hypervisors)` implementation using stevedore.

* Unit tests must also be provided to execute
  `select_destinations(self, hypervisors)`

Documentation Impact
====================

`Build a new optimization strategy` page of the generated documentation must
be updated to explain how to use the `select_destinations(self, hypervisors)`
method when implementing a new strategy.

References
==========

* [1] http://eavesdrop.openstack.org/irclogs/%23openstack-nova/%23openstack-nova.2016-02-03.log.html

* https://etherpad.openstack.org/p/mitaka-watcher-midcycle

History
=======

None

.. _Actions: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action
.. _strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
