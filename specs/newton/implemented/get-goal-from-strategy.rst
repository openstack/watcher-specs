..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================================
The achieved goal should be returned by each strategy
=====================================================

https://blueprints.launchpad.net/watcher/+spec/get-goal-from-strategy


Problem description
===================

Today, there is no way to know what `Goal`_ is achieved by a given
`Strategy`_. The mapping between goal and strategies is done in the Watcher
configuration.

Beyond that, there is no way to know that several strategies achieve the same
optimization goal.

There should be a way to return the list of available goals depending on which
strategies have been deployed on the node where the `Watcher Decision Engine`_
is running.

Use Cases
----------

As an `Administrator`_
I want to be able to get the list of available optimization goals
So that I can select one `Goal`_ and use it in my `Audit Template`_

As an `Administrator`_
I want to be able to install new strategies and get an updated list of
available goals
So that I am sure that the returned list of goals is aligned with the deployed
strategies

As an `Administrator`_
I want to be notified when the `Goal`_ of an `Audit Template`_ is not any more
available
So that I know that I have to update or delete this `Audit Template`_

As an `Administrator`_
I want to be able to get the translated name of each `Goal`_
So that I can understand what kind of optimization(s) it provides

As an `Administrator`_
I want to be able to get the list of available strategies for a given `Goal`_
So that I can select a specific strategy for my `Audit Template`_

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.


Proposed change
===============

Each `Strategy`_ should be able to return the `Goal`_ it achieves.

All strategies related to the same `Goal`_ should derive from the same parent
class and return the same `Goal`_ properties.

Below you will find a class diagram showing a hierarchy of Strategies for
several goals:

.. image:: /images/class_diagram_goal_from_strategy.png
   :width: 140%

In the future, it will also enable Watcher strategies to provide other common
attributes and methods for a given goal (input parameters, efficacy indicators,
...).


The synchronization of goals consists in establishing
data consistency between goals and strategies
automatically found by the `DefaultLoader` class
via the function `list_available` to then applying the changes in
the `Watcher database`_.
Harmonization of the goals over time should be automatically performed
by the decision_engine during start.
We should create a `Synchronizer` class which compares records
in `Watcher database`_  with those found by the `DefaultLoader`.
Then, altered goals and strategies will be replaced in order to establish
identity between the entry points and the `Watcher database`_.
As a result of the synchronization, all the available goals
and strategies are updated.
The synchronization is required for two main reasons.
The first reason is that we don't want a strong coupling between
the Watcher API component and the Watcher Decision Engine component.
In fact, we want the watcher-api only interact with `Watcher database`_
and the message broker.
The synchronization avoids the watcher cli having to call the watcher-api
which would then have to call the watcher-decision-api,
which is in charge of listing the resources.
The second one is performance and HA.

Below the strategy class and sequence diagram for syncing the goals.

.. image:: /images/get_goal_from_strategy_class_diagram.png
   :width: 140%


Alternatives
------------

Keep the current system which reads the mapping between goals and strategies
from the Watcher configuration file.

Data model impact
-----------------

The list of available goals should be stored in the `Watcher database`_.
For each goal, the list of available strategies should also be stored in the
`Watcher database`_. A new table should be created in the database for this.
Therefore a new table should be created in the database for this.
The proposed modification in the `Watcher database`_.
is illustrated on the diagram below:

.. image:: /images/get_goal_from_strategy_class_diagram.png
   :width: 140%

In the audit_template object, the 'strategy' attribute is optional.
If the admin wants to force the trigger of a `Strategy`_ it could
specify the `Strategy`_ uuid in the `Audit Template`_.
There may be several strategies applying for a given optimization `Goal`_.
If the admin didn't specify a `Strategy`_, the watcher strategy
selector is responsible for selecting an appropriate
one given the provided `Goal`_.
This blueprint should reuse the ``DefaultStrategySelector`` class
that is currently responsible for selecting the strategy.
This selection of the strategy is complex but likely
outside the scope of this blueprint (`watcher-strategy-selector`_).
However, we need to provide a basic/minimum strategy selector.
So, the strategy selector will select the first available strategy
for a given goal.
In the future, we plan have a more complex strategy selector
that would be able to select the strategy depending on many
parameters such as the usage of infrastructure, workloads, etc.

The soft delete is a commonly-used pattern and cascading must be
implemented in order to maintain integrity.
If a strategy is deleted, we need to update every audit
template linked to this strategy and setting
the strategy id to None. So the audit template can still achieve the same
goal but with a different strategy.
However, if we delete a goals we didn't plan to maintain the integrity
as it is outside the scope of this blueprint (`soft-delete-goals`_)

Note: The id attribute is used by oslo.db to handle the soft_delete feature.



REST API impact
---------------

There will be an impact on every REST resource URLs that starts with
**/v1/goals/** and that uses the type **Goal**:

* GET /v1/goals
* GET /v1/goals/(goal_uuid)
* GET /v1/goals/detail

The type **Goal** will contain two attributes:

* The unique goal id.
* The display name of the goal: i.e. the translated name of the `Goal`_ in the
  language of the `Administrator`_.

Here is a sample of the new JSON payload for a list of 2 goals, the first goal
having only one strategy and the second goal having 2 available strategies:

::

  {
      "goals": [
          {
              "goal_id": "REDUCE_ENERGY",
              "goal_display_name": "Reduce Energy Consumption",
              "strategies": [
                  {
                    "strategy_id": "POWERING_DOWN",
                    "strategy_display_name": "Powering down unused compute
                    nodes",
                  }
              ]
          },
          {
              "goal_id": "SERVERS_CONSOLIDATION",
              "goal_display_name": "Reduce the number of compute nodes needed
              to support current projects workloads"
              "strategies": [
                  {
                    "strategy_id": "FFD",
                    "strategy_display_name": "First-Fit Decreasing",
                  },
                  {
                    "strategy_id": "BFD",
                    "strategy_display_name": "Best-Fit Decreasing",
                  }
              ]
          }
      ]
  }

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

**python-watcherclient** should be able to return all goal attributes when
requesting the list of goals and to return the list of available strategies
when requesting the detail of a given goal.

It should also be possible to browse the list of available goals in **Horizon**
when the admin is creating a new `Audit Template`_. When the admin has selected
a given goal, he/she should be able to see the list of available strategies for
this goal and select the preferred `Strategy`_.

Performance Impact
------------------

None

Other deployer impact
---------------------

Now the association between a `Goal`_ and a `Strategy`_ should no more be
configured in the main Watcher configuration file.

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  vincent-francoise

Other contributors:
jed56

Work Items
----------

Here is the list of foreseen work items:

* Remove the previous `Goal`_ listing and mapping mechanism which was read from
  the Watcher configuration file. The following Python files should be
  impacted:

  - ``/devstack/local.conf.controller``
  - ``/watcher/decision_engine/strategy/selection/default.py``
  - | ``/watcher/tests/decision_engine/strategy/selector/``
    | ``test_strategy_selector.py``
  - ``/watcher/tests/api/v1/test_goals.py``
  - ``/watcher/tests/api/v1/test_audit_templates.py``
  - ``/watcher/api/controllers/v1/goal.py``
  - ``/watcher/api/controllers/v1/audit_template.py``
  - ``/watcher/opts.py``
  - ``/etc/watcher/watcher.conf.sample``
* In the ``BaseStrategy`` class, the following attributes should be added:

  - The unique goal id.
  - The display name containing the name of the goal translated in the language
    of the `Administrator`_.
  - The unique strategy id.
  - The display name containing the name of the `Strategy`_ translated in the
    language of the `Administrator`_.
* For each **XYZ** `Goal`_, there should be a base `Strategy`_ class, named
  **XYZBaseStrategy**, containing the goal attribute values indicating what
  goal id and display name all child strategies achieve.
* Update all existing strategies with this new way of handling goals. Create a
  base strategy class for each common optimization `Goal`_.
* add a new **Goal** object in **/watcher/db/sqlalchemy/models.py** for the
  storage of goals in the `Watcher database`_.
* add a new **goal.py** class in the **/watcher/objects/** package to handle
  CRUD operations on goal objects in the database.
* when the `Watcher Decision Engine`_ service is started, Watcher should browse
  the list of available strategies, get their `Goal`_ attributes and create a
  new entry in the `Watcher database`_ for each new goal id. After that, the
  `Watcher Decision Engine`_ should be able to check whether all audit
  templates in the `Watcher database`_ contain an existing goal. If not, an
  error should be traced in the logs. During this phase, the
  `Watcher Decision Engine`_ should also create a record in the database for
  each new `Strategy`_ id and associate this record to the `Goal`_ object it
  achieves. Note that this very same model would then be used by other
  blueprints such as `blueprint optimization-threshold`_ to expose the input
  parameters of each `Strategy`_.
* update the Watcher devstack plugin setup to adapt it (remove the auto
  **[watcher_goals]** config setup).

Dependencies
============

None

Testing
=======

* Update unit tests in the `Watcher Decision Engine`_
* Update Tempest test to run a strategy
* Add some Tempest tests to get the list of available goals and for each
  `Goal`_ the list of available strategies

Documentation Impact
====================

* Update the page named "*Build a new optimization strategy*" explaining that
  when a new goal is added, a new base strategy class should be created.
* Update the page named "*Configuring Watcher*", removing the "*Goals mapping
  configuration*" section.
* Update the page named "*Watcher User Guide*", providing CLI examples showing
  how to get the list of goals and how to get the list of available strategies
  for a given `Goal`_.

References
==========

IRC discussions:

* http://eavesdrop.openstack.org/meetings/watcher/2016/watcher.2016-01-20-14.00.log.html
* http://eavesdrop.openstack.org/meetings/watcher/2016/watcher.2016-02-17-14.00.log.html
* http://eavesdrop.openstack.org/meetings/watcher/2016/watcher.2016-03-16-14.00.log.html

History
=======

None


.. _Administrator: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#administrator
.. _Goal: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#goal
.. _Audit Template: http://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit-template
.. _Strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Watcher Decision Engine: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-decision-engine
.. _Watcher database: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-database
.. _blueprint optimization-threshold: https://blueprints.launchpad.net/watcher/+spec/optimization-threshold
.. _watcher-strategy-selector: https://blueprints.launchpad.net/watcher/+spec/watcher-strategy-selector
.. _soft-delete-goals: https://blueprints.launchpad.net/watcher/+spec/soft-delete-goals
