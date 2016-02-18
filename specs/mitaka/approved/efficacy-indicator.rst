..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================
Efficacy Indicator
==================

https://blueprints.launchpad.net/watcher/+spec/efficacy-indicator

Provide efficacy indicators associated with an `Audit`_ to give tangible
indicators of the possible improvement of the proposed optimization.

When the `Administrator`_ trigger an audit using Watcher, we provide a list of
`Actions`_ that should be run to attain a specific `goal`_ (defined in the
`audit template`_).
Today, there is no incentive to give a predicted result of the optimization
after running the `action plan`_. This feature will give the admin an
estimated gain of running Watcher on its infrastructure.

Problem description
===================

Today, Watcher does not provide efficacy indicators to give more accuracy to
an action plan. An administrator would require to have an idea of the level
of optimization Watcher can provide. The indicators must be related to the
initial goal set in the audit template,for example if the goal is "thermal
optimization", we should provide an estimated average inlet temperature of the
cluster (or an estimated decrease in % of the average inlet temperature).
If the `Strategy`_ applied is "basic consolidation", we should be able to
provide an estimated average CPU load after running the optimization.
These indicators must be computed by the chosen strategy.

There should also be a way to compare the efficacy of different strategies for
a given optimization `goal`_. Therefore, all the strategies associated to a
given goal should provide the same efficacy indicators so that the
`Administrator`_ can decide which strategy is the best. In the longer run, it
will also enable Watcher to automatically decide which strategy to use (via
some *StrategySelector* component in the `Watcher Decision Engine`_).


Use Cases
----------

As an administrator, I would like to have efficacy indicators to be able to
judge if the proposed optimization fit my objectives before running the
recommended action plan.

As an administrator, I would like to be able to compare the efficacy of
several strategies for the same optimization goal

As a strategy developer, I will provide a list of indicators that can be
evaluated during the execution of the audit and displayed to the administrator
with the corresponding action plan.

As a developer, I would like to make sure that all strategies associated to
a given goal provide the same list of efficacy indicators.


Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

An hashmap should be added to the `action plan`_ providing a list of efficacy
indicators with a name and a value (the name of the indicator is used as the
key for the hash map and should be unique).

We propose to use the `DDD Specification Pattern`_ to express the constraints
regarding efficacy indicators for a given `goal`_.

For each XYZ `goal`_, we should create a **XYZEfficacySpecification** class
which contains the list of expected efficacy indicators. This class would
contain the following properties for each expected efficacy indicator:

- the name of the indicator, which must be translated via i18n oslo lib
- a description, which must be translated via i18n oslo lib
- the unit of the indicator (percent, kWh, second, ...), which must be
  translated via i18n oslo lib
- the type of the value (integer, float, enum, string, ...) and range of
  allowed values.
- a flag indicating whether it is mandatory or optional

Each strategy associated to a given XYZ goal should have access to a
singleton of the **XYZEfficacySpecification** class in order to make sure
the generated action plan contains the expected efficacy indicators. In other
words, in each strategy, it should be possible to call the
**checkEfficacyIndicators(ActionPlan)** method of the
**XYZEfficacySpecification** which returns a boolean saying whether all
mandatory efficacy indicators are provided in a given `action plan`_ and
whether the indicator values are compliant with the expected types and ranges.

It should be possible to call a **getGlobalEfficacy(ActionPlan)** method from
the **XYZEfficacySpecification** class which returns a global score of efficacy
for a given `action plan`_. This global score would be computed using a
ponderated sum of the different efficacy indicators.

Below you will find a class diagram showing the hierarchy of Strategies for
several goals and how they are related to efficacy specification classes:

.. image:: ../../../doc/source/images/class_diagram_efficacy_indicator.png
   :width: 140%

In the future, the `DDD Specification Pattern`_ will enable Watcher to compose
several efficacy indicators whenever an Audit is launched with multiple goals.


Alternatives
------------

The administrator will let Watcher do the optimization without having a
forecast of the potential gain on the infrastructure.

Data model impact
-----------------

The following data object will be impacted:

* **ActionPlan**:

  * We may need to store in the database a list of efficacy indicators
    associated with the action plan (hashmap)


REST API impact
---------------

There will be an impact on every REST resource URLs that starts with
**/v1/action_plans/** and that uses the type **ActionPlan**:

* GET /v1/action_plans
* GET /v1/action_plans/(action_plans_uuid)
* POST /v1/action_plans
* DELETE /v1/action_plans
* PATCH /v1/action_plans
* GET /v1/action_plans/detail

The type **ActionPlan** will contain a new **efficacy** object with a hashmap
of indicators.

Here is a sample of the new JSON payload for an action plan which includes
the **efficacy** object composed of one global efficacy indicator and three
detailed indicators:

::

  {
      "action_plans": [
          {
              "audit_uuid": "abcee106-14d3-4515-b744-5a26885cf6f6",
              "first_action_uuid": "57eaf9ab-5aaa-4f7e-bdf7-9a140ac7a720",
              "links": [
                  {
                      "href": "http://localhost:9322/v1/action_plans/9ef4d84c-41e8-4418-9220-ce55be0436af",
                      "rel": "self"
                  },
                  {
                      "href": "http://localhost:9322/action_plans/9ef4d84c-41e8-4418-9220-ce55be0436af",
                      "rel": "bookmark"
                  }
              ],
              "state": "ONGOING",
              "updated_at": "2016-02-08T12:59:33.445869",
              "uuid": "9ef4d84c-41e8-4418-9220-ce55be0436af",
              "efficacy" : [
                  {
                      "name" : "Global efficacy score",
                      "value" : "89"
                  },
                  {
                      "name" : "Average CPU load",
                      "value" : "22"
                  },
                  {
                      "name" : "Average inlet temperature",
                      "value" : "34"
                  },
                  {
                      "name" : "Number of sleeping hosts",
                      "value" : "2"
                  }
              ]
          }
      ]
  }

There will also be an impact on every REST resource URLs that starts with
**/v1/goals/** and that uses the type **Goal**:

* GET /v1/goals
* GET /v1/goals/(goal_uuid)
* GET /v1/goals/detail

The type **Goal** will contain a new **efficacy_specification** object with a
hashmap of indicator descriptions.

Here is a sample of the new JSON payload for a goal which includes
the **efficacy_specification** object composed of 4 indicators:

::

  {
      "goals": [
          {
              "name": "Reduce Energy Consumption",
              "efficacy_specification" : [
                  {
                      "name" : "Relative energy gain",
                      "description" : "The amount of gained energy in %",
                      "unit" : "%",
                      "type" : "integer",
                      "range" : "[0..100]",
                      "mandatory" : "true"
                  },
                  {
                      "name" : "Absolute energy gain",
                      "description" : "The amount of gained energy in kWh",
                      "unit" : "kWh",
                      "type" : "long",
                      "mandatory" : "true"
                  },
                  {
                      "name" : "Number of VM migrations",
                      "description" : "The total number of VM to migrate",
                      "unit" : "counter",
                      "type" : "integer",
                      "mandatory" : "true"
                  },
                  {
                      "name" : "Estimated action plan duration",
                      "description" : "The estimated time needed to execute the
                      action plan, in seconds",
                      "unit" : "second",
                      "type" : "long",
                      "mandatory" : "true"
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

Efficacy indicators needs to be added to the python-watcherclient to provide
extra information when requesting action plans or goals.

The indicators must also be added to watcher-dashboard to allows the cloud
administrator to take appropriate decision in Horizon.

Performance Impact
------------------

The calculation of efficacy indicators will be done by the targeted
strategy, we should keep in mind that this calculation must not add delay to
the building of the actions plan.

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
  <launchpad-id or None>

Other contributors:
  v-mahe, jed56, acabot

Work Items
----------

Here is the list of foreseen work items:

* add a field to action-plan object to store the list of efficacy indicators
* implement an example of efficacy specification class which contains a
  description of the expected efficacy indicators for a given goal and the
  needed methods:

  - **checkEfficacyIndicators(ActionPlan)**
  - **getGlobalEfficacy(ActionPlan)**
* implement a base class dedicated to a goal that will hold a list of possible
  strategies and an efficacy specification.


Dependencies
============

There are some dependencies with the following blueprint:

* https://blueprints.launchpad.net/watcher/+spec/get-goal-from-strategy : if
  there is a base class **XYZBaseStrategy** for all strategies associated to
  the same XYZ goal, the **XYZEfficacySpecification** should be associated to
  this base class.

There is also a dependency with the following bug:

* https://bugs.launchpad.net/watcher/+bug/1546630 : the API documentation
  should explain how to request the list of available goals and for each goal
  it should be possible to see the list of efficacy indicators.

Testing
=======

* Unit tests on the `Watcher Decision Engine`_
* Tempest test to run a strategy to get efficacy indicators
* Tempest test to get the list of available goals and for each goal the list
  of efficacy indicator specification.
* An admin should be able to launch an Audit with Watcher with a
  BASIC_CONSOLIDATION goal on an OpenStack cluster and get efficacy
  indicators associated with the generated action plan.


Documentation Impact
====================

None


References
==========


History
=======

None


.. _Audit: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit
.. _Administrator: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#administrator
.. _Actions: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action
.. _goal: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#goal
.. _audit template: http://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit-template
.. _action plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Watcher Decision Engine: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-decision-engine
.. _DDD Specification Pattern: http://martinfowler.com/apsupp/spec.pdf
