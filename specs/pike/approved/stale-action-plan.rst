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

Three scenarios need to be considered:

SCENARIO_1 action plan expiry
------------------------------

If an action plan remains in the RECOMMENDED state for a specified
amount of time (24 hours by default), the state will automatically
be set to SUPERSEDED.

for example:
::

  actionplan_1{created_at:'2017-02-07 01:00:00', state:RECOMMENDED}
  actionplan_2{created_at:'2017-02-07 02:00:00', state:RECOMMENDED}

  when datetime='2017-02-08 01:01:00'
  (datetime-actionplan_1.created_at)>24 hours
  (datetime-actionplan_2.created_at)<24 hours
  result:
  actionplan_1{created_at:'2017-02-07 01:00:00', state:SUPERSEDED}
  actionplan_2{created_at:'2017-02-07 02:00:00', state:RECOMMENDED}

  when datetime='2017-02-08 02:01:00'
  (datetime-actionplan_1.created_at)>24 hours
  (datetime-actionplan_2.created_at)>24 hours
  result:
  actionplan_1{created_at:'2017-02-07 01:00:00', state:SUPERSEDED}
  actionplan_2{created_at:'2017-02-07 02:00:00', state:SUPERSEDED}

SCENARIO_2 action plan launch
------------------------------

When a **RECOMMENDED** action plan is launched successfully, other
action plans that are still in the **RECOMMENDED** state will be
set to **SUPERSEDED** state.

Two cases:

**CASE a:**

Regardless of the scope of the audit generated action plan, as long as
the action plans state are **RECOMMENDED**, will be set to **SUPERSEDED**.

for example:
::

    scope_1 = {'availability_zones': [{'name': 'AZ1'}]}
    scope_2 = {'availability_zones': [{'name': 'AZ2'}]}
    scope_3 = {'availability_zones': [{'name': 'AZ3'}]}

    actionplan_1{audit.scope:'scope_1', state:RECOMMENDED}
    actionplan_2{audit.scope:'scope_2', state:RECOMMENDED}
    actionplan_3{audit.scope:'scope_3', state:RECOMMENDED}

    when launch actionplan_1{audit.scope:'scope_1', state:SUCCEEDED}
    result:
    actionplan_2{audit.scope:'scope_2', state:SUPERSEDED}
    actionplan_3{audit.scope:'scope_3', state:SUPERSEDED}

**CASE b:**

Consider the scope of the audit that generated the action plan, check the
scope of the audit that generated the action plan, and only set the action
plan with the same scope to **SUPERSEDED**.

for example:
::

    scope_1 = [{'availability_zones': [{'name': 'AZ1'}, {'name': 'AZ2'}]}]
    scope_2 = [{'availability_zones': [{'name': 'AZ1'}, {'name': 'AZ2'}]}]
    scope_3 = [{'availability_zones': [{'name': 'AZ2'}, {'name': 'AZ1'}]}]

    actionplan_1{audit.scope:'scope_1', state:RECOMMENDED}
    actionplan_2{audit.scope:'scope_2', state:RECOMMENDED}
    actionplan_3{audit.scope:'scope_3', state:RECOMMENDED}

    when launch actionplan_1{audit.scope:'scope_1', state:SUCCEEDED},
    scope_1==scope_2:True
    scope_1==scope_3:False
    result:
    actionplan_2{audit.scope:'scope_2', state:SUPERSEDED}
    actionplan_3{audit.scope:'scope_3', state:RECOMMENDED}

**notice:**
*The audit.scope string value is compared here.*
*So the result of scope_1 and scope_3 comparison is false.*

SCENARIO_3 data model change
-----------------------------

When the node in the data model changes, the action plan in the
**RECOMMENDED** state is set to **SUPERSEDED** state.

Two cases:

**CASE a:**

As long as there is a node change, the action plan in the **RECOMMENDED**
state will be set to **SUPERSEDED** state.

for example:
::

    scope_1 = {'availability_zones': [{'name': 'AZ1'}]}
    scope_2 = {'availability_zones': [{'name': 'AZ2'}]}
    scope_3 = {'availability_zones': [{'name': 'AZ3'}]}

    actionplan_1{audit.scope:'scope_1', state:RECOMMENDED}
    actionplan_2{audit.scope:'scope_2', state:RECOMMENDED}
    actionplan_3{audit.scope:'scope_3', state:RECOMMENDED}

    when any node in data model change
    result:
    actionplan_1{audit.scope:'scope_1', state:SUPERSEDED}
    actionplan_2{audit.scope:'scope_2', state:SUPERSEDED}
    actionplan_3{audit.scope:'scope_3', state:SUPERSEDED}

**CASE b:**

Check the audit scope of the generated action plan. Only when the node
which in the scope of the audit, the corresponding action plan is set
to **SUPERSEDED**.

for example:
::

    scope_1 = {'availability_zones': [{'name': 'AZ1'}]}
    scope_2 = {'availability_zones': [{'name': 'AZ2'}]}
    scope_3 = {'availability_zones': [{'name': 'AZ3'}]}

    actionplan_1{audit.scope:'scope_1', state:RECOMMENDED}
    actionplan_2{audit.scope:'scope_2', state:RECOMMENDED}
    actionplan_3{audit.scope:'scope_3', state:RECOMMENDED}

    when node in scope_1 change
    result:
    actionplan_1{audit.scope:'scope_1', state:SUPERSEDED}
    actionplan_2{audit.scope:'scope_2', state:RECOMMENDED}
    actionplan_3{audit.scope:'scope_3', state:RECOMMENDED}

**Discussion conclusion**
As below there are three options to choose from.
According to the conclusion at the PTG meeting, at first we do
the simple one, and take scope into consideration where needed
in future work.

**1:** Simple, just SCENARIO_1

**2:** Stringent, SCENARIO_1 + SCENARIO_2a + SCENARIO_3a

**3:** Complex, SCENARIO_1 + SCENARIO_2b + SCENARIO_3b

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

Add new config parameter **action_plan_expiry** and
**check_periodic_interval**.
::

    cfg.IntOpt('action_plan_expiry',
               default=24,
               help=('An expiry date(hours). We invalidate the action plan'
                      'if its created older than the expiry date.')),
    cfg.IntOpt('check_periodic_interval',
               default=30*60,
               help=('Seconds between running periodic tasks.'))

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

* Add config parameter **action_plan_expiry** and
  **check_periodic_interval**(SCENARIO_1).
* Modify the **DefaultActionPlanHandler** class, trigger to check the state
  of action plan(SCENARIO_2).
* Currently, when receives the specific event (such as nova notification
  event_type:service.update, instance.update, instance.delete.end), the
  decision engine will update the cluster data model. We need to add the state
  of action plan updates to this process(SCENARIO_3).
* Add a new **StateManager** class. In this class, we implement the action
  plan state management(SCENARIO_1, SCENARIO_2, SCENARIO_3).

Dependencies
============

https://blueprints.launchpad.net/watcher/+spec/define-the-audit-scope

Testing
=======

The unit tests and tempest test will have to be updated.

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

