..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================================
Add support to cancel execution of Action Plan
==============================================

https://blueprints.launchpad.net/watcher/+spec/cancel-action-plan

Problem description
===================

A Cloud `Administrator`_ may want to cancel the `action plan`_ execution for
any reason. An Action Plan can be in execution from long time and a cloud
Administrator may want to execute the actions manually or want to fulfill the
optimization requirements by some other methods.

As of now Administrator can update the action plan state to **CANCELLED** but
there is no action taken by Watcher to cancel the action plan. It only updates
the action plan state to **CANCELLED**.

It should be possible to **CANCEL** execution of the action plan by Watcher.

Use Cases
----------

As a Watcher Administrator, I want Watcher to CANCEL the action plan that is
in ONGOING state for a long time.

As a Watcher Administrator, I want to CANCEL any action plan that is
accidentally launched.

As a Watcher Administrator, I want to CANCEL the action plan because my
optimization requirements have been met.

Proposed change
===============

* Add  new state  **CANCELLING** for the **Action Plan**.

  * CANCELLING, when watcher-api receives request from cloud admin to cancel
    the **ONGOING** action plan. When watcher-applier successfully executed
    the cancel request it will update the action plan state to **CANCELLED**.
    When watcher-applier failed to complete the action plan cancel request, it
    will update the action plan state to **FAILED**.

* Add new states **CANCELLING**, **CANCELLED** to **Action**.

  * CANCELLING, when watcher-applier cancel an ONGOING action.

  * CANCELLED, when watcher-applier cancel a PENDING action. when
    watcher-applier successfully completed cancel of ONGOING action.

* Add a new command **watcher actionplan cancel** in watcher-client to cancel
  the action plan.

* Modify the state machine for action plan to add new actions plan state and
  transitions.

* Modify the state machine for action to add new actions states and
  transitions.

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

https://blueprints.launchpad.net/watcher/+spec/notifications-actionplan-cancel

Other end user impact
---------------------

A new command **watcher actionplan cancel** will be added to cancel the action
plan.

Performance Impact
------------------

None

Other deployer impact
---------------------

Watcher cannot guarantee about the cluster state after cancelling the ongoing
optimizations.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <adi-sky17>

Work Items
----------

* Implementation for action plan cancel will be done by using taskflow. When a
  running engine receives an exception, it stops execution and calls revert
  method for all the tasks(actions) added in the flow. In the revert method of
  action, current action state is checked and based on the action state
  (PENDING, ONGOING, SUCCEEDED) revert method will execute defined steps.

  .. code-block:: python

      e.g. if action_state is PENDING:
            # update action_state to CANCELLED
           if action_state is ONGOING:
            # call abort_action
           if action state is SUCCEEDED:
            # do nothing

* Before starting any new action watcher-applier will check for the state of
  action plan, if its state is updated to CANCELLING it will trigger an
  exception "ActionPlanCancel" to the taskflow engine and taskflow engine will
  call revert method of all tasks (actions) in reverse manner, keeping the
  dependencies intact.

Dependencies
============

For action plan cancel operation we need to call Abort API for **ONGOING**
actions.

The abort API of live migration is available.
https://blueprints.launchpad.net/nova/+spec/abort-live-migration

The abort API for cold migration is under development.
https://blueprints.launchpad.net/nova/+spec/abort-cold-migration

Testing
=======

The unit and tempest tests will have to be updated.

Documentation Impact
====================

Need to update the **Action Plan State Machine** in the architecture
documentation.

Need to add the **Action State Machine** in the architecture documentation.

References
==========

.. _Administrator: https://docs.openstack.org/developer/watcher/glossary.html#administrator-definition
.. _action plan: https://docs.openstack.org/developer/watcher/glossary.html#action-plan

History
=======

None

