..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================================
Multiple global efficacy indicator
==================================

https://blueprints.launchpad.net/watcher/+spec/multiple-global-efficacy-indicator

Problem description
===================

Watcher calculates global-efficacy as a single value with available efficacy
indicators. It is useful for those strategies which optimizes only one
openstack resource. For strategies that optimizes multiple resources, multiple
global efficacy indicator is required, as each global efficacy indicator will
represent one resource.
e.g. There are two strategies which optimizes storage and compute both,
cloud admin checks the value of global efficacy for both strategy and decides
to choose which is higher. cloud admin actually wants to choose strategy which
has better compute optimization, since global efficacy is single entity it
will not be able to reflect only compute optimization. There is a possibility
that user may choose higher global effiacy strategy but at reality its value
is higher because of storage efficacy. so its better to have multiple global
efficacy indicator one for each resource.


Use Cases
----------

As a Watcher user, For better selection of strategies I want to have multiple
global efficacy indicating each resource.

Proposed change
===============

* Initialize global efficacy as list in Efficacy class.

* Return global efficacy in following format from EfficacySpecification.
  It will be a list of objects of efficacy.Indicator class::

   [(efficacy.Indicator(name='', description='', unit='', value='')),
    (efficacy.Indicator(name='', description='', unit='', value='')),
   ]

* Change the parsing of format_global_efficacy method in python-watcherclient

* Change ActionPlan Data model, as global efficacy was a JSONEncodedDict
  before and now it will be JSONEncodedList .

Alternatives
------------

We can keep global efficacy as single entity,let user calculate multiple
values based on resource using efficacy indicators.

Data model impact
-----------------

None

REST API impact
---------------

global efficacy JSON schema will change. It will affect follwing API's::

    GET /v1/action_plans/(action_plan_uuid)
    GET /v1/action_plans/detail
    GET /v1/action_plans

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
  <adi-sky>

Other contributors:
  <None>

Work Items
----------

* Initialize global_efficacy as list in
  watcher.decision_engine.solution.efficacy.Efficacy
* Update ActionPlan data model.
* Update the method get_global_efficacy_indicator in
  watcher.decision_engine.goal.efficacy.specs.ServerConsolidation
* Update in python-watcherclient.

Dependencies
============

None

Testing
=======

Unit test will be updated.

Documentation Impact
====================

Update the contributor guide for goal plugin.
https://docs.openstack.org/watcher/latest/contributor/plugin/goal-plugin.html#implementation

References
==========

* https://docs.openstack.org/watcher/latest/glossary.html#efficacy-indicator
