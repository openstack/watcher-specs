..
   This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================
Rollback Mechanism
===================

https://blueprints.launchpad.net/watcher/+spec/rollback-mechanism


Problem description
===================

After every audit, there would be one actionplan to execute. The actionplan
is a group of actions, such as:

 * migrations
 * change nova service state
 * change node power state
 * ...

Sometimes, the users want to rollback one actionplan even after the actionplan
successfully executed.

To tester, they usually make the env unbalance, so that there will be
instances migration during audit. After that they need to migrate
the instances back to the source host for next test.

Moreover, for host maintenance, it will migrate all instances from the
maintaining host to others. After the host maintenance and active again,
there is no mechanism to migrate the instances automatically back to the
maintaining host.

Use Cases
----------

As a QA of Watcher, I want to rollback the actionplan, so that I can easily
restore the environment for next test.

As an openstack operator, I want to migrate the instances back to the source
node after the node having been executed "host maintenance" strategy.

Proposed change
===============

In watcher-api, we can add 'rollback' action to ActionPlan API. When the api
recieves the rollback request and then distributes the request to
watcher-decision-engine module.

In watcher-decision-engine, it retrives the actionplan and records every
rollback of the actions which belong to the actionplan, then return the
rollback result to watcher-api.

Because the compute data model changes by time, the actionplan is possible to
rollback failed. To make the rollback mechanism to work as far as possible,
only recent(default, recent in one hour) actionplan is allowed to rollback.

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

Rollback Action Plan

* /v1/action_plans/{actionplan_ident}/rollback

  * Method type: POST

  * actionplan_ident：UUID of the Action Plan

  * Normal http response code(200)

  * Expected error http response code(400,404)

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
  <sue>

Work Items
----------

* ActionPlan rollback action API

* RollBack mechanism for one actionplan

Dependencies
============

None

Testing
=======

Unit tests

Documentation Impact
====================

* Add documentation about how to use the new feature

References
==========

None

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Ussuri
     - Introduced
