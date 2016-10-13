..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===========================================
Define when an action plan is stale/invalid
===========================================

https://blueprints.launchpad.net/watcher/+spec/stale-action-plan

Problem description
===================

When an audit is created and launched successfully, it generates a new
action plan with status **RECOMMENDED**. If the cluster data model has changed
by and by, the action plan still remains in the **RECOMMENDED** state. There is
not an expiry date or event that can invalidate the action plan so far.

It should be possible to add a new **SUPERSEDED** state for action plan.

Use Cases
----------

As a Watcher Administrator, I want watcher to update the state of any action
plan from **RECOMMENDED** to **SUPERSEDED** automatically if the action plan
has expired (default expiry time: 24 hours).

As a Watcher Administrator, after the recommended action plan is launched
successfully, I want watcher to update the state of any action plan based on
the same cluster data model from **RECOMMENDED** to **SUPERSEDED**
automatically.

As a Watcher Administrator, when the cluster data model changes, I want watcher
to update the state of action plan based on this cluster data model from
**RECOMMENDED** to **SUPERSEDED** automatically.

Project Priority
-----------------

None

Proposed change
===============

* Add a new state **SUPERSEDED** for the **Action Plan**.
* Add a new config parameter **action_plan_expiry**, This parameter is
  used to set the time interval for checking the state of action plan.
  Its type is Integer and the value is **24** (hours) by default.
* Add a new **CheckActionplanState** class. In this class we use the
  **APScheduler** library to check the state of action plan periodically.
  **APScheduler** is a Python library that can schedule a job to be executed
  later, either just once or periodically. It has been used in the continuous
  audits, we just add our new job in the scheduler. The interval of the
  periodic job is configurable.
* Modify the **DefaultActionPlanHandler** class, trigger to check the state
  of action plan.
* Currently, when receives the specific event (such as nova notification
  event_type:service.update, instance.update, instance.delete.end), the
  decision engine will update the cluster data model. We need to add the state
  of action plan updates to this process. To identify the action plan affected
  by the cluster data model change, we distinguish by **audit.scope** field.
  Only when the cluster data in the audit scope has changed, we update the
  state of action plan. If audit.scope is null, we still update the state of
  action plan when any cluster data is changed.

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

None

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <licanwei>

Work Items
----------

Here is the list of foreseen work items:

* Add a **SUPERSEDED** state to the class **State** in the file
  **watcher/objects/action_plan.py**.
* Update the **DefaultActionPlanHandler** class in **watcher/applier/
  action_plan/default.py**.
* Add a **manager.py** file to the **watcher/common** folder.
* Add check_state code in the file **watcher/decision_engine/scheduling.py**.
* Add check_state code in the file **watcher/decision_engine/model/
  notification/nova.py**.

Dependencies
============

https://blueprints.launchpad.net/watcher/+spec/define-the-audit-scope

Testing
=======

The unit tests will have to be updated.

Documentation Impact
====================

Need to update the **Action Plan State Machine** in the architecture
documentation.

References
==========

None

History
=======

None

