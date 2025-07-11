..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================================================================
Add a mechanism to skip Watcher Actions when running an action plan
======================================================================

https://blueprints.launchpad.net/watcher/+spec/add-skip-actions

The Watcher service should allow to exclude actions from an Action Plan
execution in two situations:

*  A cloud admin explicitly wants to exclude an action or set of actions from
   execution before starting an action plan.
*  Watcher applier detects the object where the action is applied to be in a
   state where the action should not be applied. For example, in a migrate
   action, the instance does not longer exist.

Problem description
===================

Currently Watcher does not provide a way to exclude actions execution when
running an action plan:

* Administrators lack a standardized mechanism to preemptively skip
  actions.
* Pre-condition failures are not clearly distinguished from execution
  failures.

Note that Actions already include the CANCELLED state in `its state machine
<https://github.com/openstack/watcher/blob/f38ab70ba46756b2c3ae74b1a2fafdb39ac58cc7/watcher/api/controllers/v1/action.py#L38-L51>`_
however, it is only used for two specific cases:

* When an Action Plan is cancelled, all the actions included are moved to the
  CANCELLED state.
* When the watcher-applier process is started, all the actions assigned to it
  in ONGOING state are moved to CANCELLED state (see `this link <https://github.com/openstack/watcher/blob/59607f616a0a7c8e38f488922ec3c27dffe692e7/watcher/applier/sync.py#L54-L75>`_ ).

The purpose of this spec is to document the required changes in Watcher to
implement the Actions execution exclusion in the two mentioned use cases.

Use Cases
----------

* **Admin Override:** Administrators can use a patch API call to move an action
  state from PENDING to SKIPPED, so the action will not be executed when
  the action plan is executed.
* **Pre-condition detection:** When the pre_condition method of an action
  returns a specific type of Exception, the action will be moved to SKIPPED
  and execution and post_conditions will not be executed.

In both cases, a `status_message` may be provided and stored in the database.
Similarly a `status_message` field will be added to the ActionPlan object that
will be used to provide information about skipped actions. For consistency the
`status_message` will be also added to the Audit object which will be used in
future to store information related to status changes.

Proposed change
===============

Currently, the watcher state machine for Actions from PENDING state provides
following transitions:

* PENDING -> CANCELLED (action plan is cancelled before action is started)
* PENDING -> ONGOING (start action execution)
* ONGOING -> CANCELLED (action plan is cancelled while action is running)
* ONGOING -> SUCCEEDED (action finishes successfully)
* ONGOING -> FAILED (action execution failed)

The proposed change in this spec is to add a new state `SKIPPED` which would
imply that an action is being excluded from an Action Plan execution for any
of the mentioned use cases.

After this change, additionally, the state machine for Actions will allow
following state transition:

* PENDING -> SKIPPED (action is excluded from execution before started)
* PENDING -> FAILED (action failed in pre-condition with unexpected error)

Note that the transition from PENDING to SKIPPED can be triggered by the
cloud administrator using an API call or automatically when watcher detects
certain predefined conditions in pre_condition execution. Transitioning an
action from PENDING to ONGOING should imply that pre_condition execution
finishes successfully. An action which fails in pre_condition execution with
any error different that the predefined conditions will change the state
to FAILED before moving it to the ONGOING state.

Actions in SKIPPED state will not affect the final state of the action plan.
An action plan will only be considered to be FAILED when one or more actions
are in FAILED state when execution finishes. However, in order to provide the
user with details about the actual result of the execution, a new field will
be added to the action plan `status_message` which will be updated when one
or more actions are skipped with relevant information about the skipped
actions.

For the pre-condition detection use case, a new class of Exception
`ActionSkipException` will be created. When pre_condition raises it, the
ongoing action will be switched to SKIPPED state, and `status_message` will be
added based on the exception message.

For the admin override use case, a new api call Patch method will be added to
the Actions which will allow to change the state from PENDING to SKIPPED
state only when the parent action plan is also in the PENDING state.
In that case, a comment `skipped by user` will be included in the
`status_message`. Optionally, the user will be able to add further details to
the message.

Additionally, support for the changes in the API should be included in the
python-watcherclient and watcher-dashboard so that the cloud admins can skip
an action from PENDING state and see the `status_message` value for SKIPPED
actions.

Microversion of the Watcher API will be increased for this change as follows:

* The new action state SKIPPED will not be handled as microversioned. This
  means that the value of the action state will be identical, independently
  of the Watcher API microversion used.
* The new field `status_message` will be included in the new microversion
  both in the Action, ActionPlan and Audit objects, so it will only be
  included in the corresponding API calls when using the new microversion
  or higher. When using previous ones, the new field will not be included
  in API responses.
* New patch API calls will only be available when using the new microversion
  or newer.

Alternatives
------------

During the review of this spec, multiple aspects were discussed and decisions
made. The most important aspects were:

**SKIPPED vs reuse CANCELLED**

Instead of creating a new SKIPPED state, we may reuse the existing CANCELLED
state to cover the two new use cases. After discussing this option `on irc
<https://meetings.opendev.org/irclogs/%23openstack-watcher/%23openstack-watcher.2025-05-13.log.html#openstack-watcher.2025-05-13.log.html#t2025-05-13T12:53:54>_`.
we have considered that it would lead to ambiguity in the actual situation for
CANCELLED actions, as multiple and pretty different situations may lead to it.

With this proposal, the SKIPPED state is restricted to be used for actions
which were never actually executed in executed action plans.

**Using PATCH vs PUT or POST API calls**

An alternative approach to the proposed changes in the API in this spec was
to use POST calls on `/v1/action_plans/{plan_id}/actions/{action id or index}`.
While this would follow the best practices in terms of REST API implementation
and would be more correct to show actions as internal to ActionPlans, the
approved implementation is more consistent with the existing API methods
in Watcher and the current representation of the Actions in the API as top
level elements.

**ActionPlan state when Actions are skipped**

This spec proposal does not modify the state of a finished ActionPlan when any
of the actions included on it is skipped by user or pre_condition failure.
Additionally, the `status_message` field will be used to make users aware of
actions were skipped if so, even when the ActionPlan is in `SUCCEEDED` state
as it has been considered that it is a relevant information for the users.

Alternatives to this approach would be to create a specific field
`skipped_actions` in the `ActionPlans` to provide specifically that information
or to create a new state `SUCCEDED_WITH_SKIPPED` which would be use for
ActionPlans with automatically skipped actions.

However, it has been considered that using the new generic field
`status_message` is more appropiate and reusable to provide further details
in other situations in future (i.e. for `FAILED` actions) and the `SUCCEEDED`
state to represent correctly the real state when an action is not executed
as specifically decided by the user or automatically by watcher detecting
a condition which has been predefined to lead the action to `SKIPPED` instead
of `FAILED` state.

**Adding status_message to Audits**

Although the audits state is not directly affected by the proposed use cases,
it has been determined that the `status_message` field can be useful for the
Audits too. It has been decided to include this field in the same API
microversion for consistency among the API objects and clients.

Data model impact
-----------------

* Add a new column `status_message` of type `String(255)` in Actions table.
* Add a new column `status_message` of type `String(255)` in ActionPlans table.
* Add a new column `status_message` of type `String(255)` in Audits table.

REST API impact
---------------

In a new microversion the following API responses are extended:

* New field `status_message` will be included in actions:

  * ``GET /v1/actions/detail``
  * ``GET /v1/actions/``{action_id}``

  No changes in Return code(s).

  Example of json addition in ``GET /v1/actions/``{action_id}`` response:

  .. code-block::


      {
          "state": "SKIPPED",
          "description": "Logging a NOP message",
          "status_message": "Skipped by user",
          ....
      }

* New field `status_message` will be included in actionplans:

  * ``GET /v1/actionplans/detail``
  * ``GET /v1/actionplans/``{action_id}``

  No changes in Return code(s).

  Example of json addition in ``GET /v1/actionplans/``{actionplan_id}``
  response:

  .. code-block::


      {
          "state": "SUCCEEDED",
          "status_message": "Action XXX was skipped by user",
          ....
      }

* New field `status_message` will be included in audits:

  * ``GET /v1/audits/detail``
  * ``GET /v1/audits/``{audit_id}``

  No changes in Return code(s).

  Example of json addition in ``GET /v1/audits/``{audit_id}``
  response:

  .. code-block::


      {
          "state": "CANCELED",
          "status_message": "Audit was canceled by user",
          ....
      }

* A new Patch method on ``/v1/actions/``{action_id}`` will be added to skip
  an Action in PENDING state.

  Normal response codes: 200

  Error codes: 400,409,404

  Example Action PENDING skipping request:

  .. code-block::

      [
          {
              "op": "replace",
              "value": "SKIPPED",
              "path": "/state"
          },
          {
              "op": "add",
              "value": "Exclude migration of intance foo",
              "path": "/status_message"
          },
      ]

  Trying to patch an unexisting Action will return a 404 error.

  Request to skip an action using Patch API method in any state different
  that PENDING will return a 409 error.

  The API Patch call will allow to modify the `status_message` field for an
  action which is in SKIPPED state.


Security impact
---------------

No security impact.

Notifications impact
--------------------

The action, actionplan and audit notifications will be extended to contain the
newly added field.

Other end user impact
---------------------

Following changes will be implemented in the watcherclient:

* New field `status_message` will be included in command:

  .. code-block::

    openstack optimize action show <action id>

* New option `skip` will be added to the `optimize action` command:

  .. code-block::

    openstack optimize action update --state skipped --message <message> <action id>

Similar functionalities will be implemented in the watcher-dashboard package
to perform the same actions and get similar information from the horizon
dashboard.

Performance Impact
------------------

No performance impact expected.

Other deployer impact
---------------------

No new configuration parameter or any other impact on deployer

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  amoralej


Work Items
----------

* Add a new field to the Actions table.
* Add a new field to the Actions GET REST API
* Add a new exception type and move ongoing actions
  to SKIPPED state if pre_condition raises it.
* Add a new patch method to the actions api to skip pending actions.
* Add support in watcherclient.
* Add support in watcher-dashboard.
  * Include the new field `status_message` in the Actions and ActionPlans
  views.
  * Add a button to skip actions from the `Related Actions` in the ActionPlans
  detailed view.
  * Additionally, a `skip` button may be also added to the action detailed
  view.

Dependencies
============

None

Testing
=======

Existing unit and API tests will be extended to validate that the new
microversion contains `status_message`.

Unit tests will validate that an action raising the new exception in the
pre_condition, moves the action to SKIPPED state.

Unit tests to test new patch methods on actions.

New tempest test to test the action skipping feature, including the optional
field `status_message`.

Documentation Impact
====================

* API Reference
* REST API Version History
* watcher client

References
==========


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Flamingo
     - Description
   * - 2025.2
     - Introduced
