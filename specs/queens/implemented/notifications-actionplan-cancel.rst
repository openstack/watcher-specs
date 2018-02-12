..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
action plan cancel notifications
===================================

https://blueprints.launchpad.net/watcher/+spec/notifications-actionplan-cancel

A new operation **watcher actionplan cancel** is implemented in watcher, This
spec propses to implement notifications for watcher `action plan`_ cancel.

Problem description
===================

As of now, there is no notification implemented for
"watcher actionplan cancel" so no way to know for event based plugins, when
action plan cancel started and completed.

Use Cases
---------

As an OpenStack developer, I want to be able to listen to notifications coming
from Watcher about actionplan cancel.

As an OpenStack developer, I want to be notified whenever:

- an actionplan cancel started
- an actionplan cancel completed
- an actionplan cancel failed

As an OpenStack developer, I would also want to be notified whenever:

- `action`_ abort (cancel) started
- action abort (cancel) completed
- action abort (cancel) failed

Proposed change
===============

In order to implement the above use cases, many different notifications will
be needed:

- ``actionplan.cancel.start`` whenever an actionplan cancellation starts.
- ``actionplan.cancel.end`` whenever an actionplan cancellation ends.
- ``actionplan.cancel.error`` whenever an actionplan cancellation failed.

- ``action.cancel.start`` whenever an action is aborted.
- ``action.cancel.end`` whenever an action abort end.
- ``action.cancel.error`` whenever an action abort failed

**actionplan.cancel.start**

.. code-block:: json

    {
      "event_type": "actionvent_type": "action_plan.cancel.start",
      "payload": {
        "watcher_object.namespace": "watcher",
        "watcher_object.name": "ActionPlanCancelPayload",
        "watcher_object.version": "1.0",
        "watcher_object.data": {
          "created_at": "2016-10-18T09:52:05Z",
          "deleted_at": null,
          "audit_uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
          "audit": {
            "watcher_object.namespace": "watcher",
            "watcher_object.name": "TerseAuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.data": {
              "created_at": "2016-10-18T09:52:05Z",
              "deleted_at": null,
              "uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "scope": [],
              "audit_type": "ONESHOT",
              "state": "SUCCEEDED",
              "parameters": {},
              "interval": null,
              "updated_at": null
            }
          },
          "uuid": "76be87bd-3422-43f9-93a0-e85a577e3061",
          "fault": null,
          "state": "CANCELLING",
          "global_efficacy": {},
          "strategy_uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
          "strategy": {
             "watcher_object.namespace": "watcher",
             "watcher_object.name": "StrategyPayload",
             "watcher_object.version": "1.0",
             "watcher_object.data": {
               "created_at": "2016-10-18T09:52:05Z",
               "deleted_at": null,
               "name": "TEST",
               "uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
               "parameters_spec": {},
               "display_name": "test strategy",
               "updated_at": null
             }
           },
           "updated_at": null
          }
        },
        "priority": "INFO",
        "message_id": "3984dc2b-8aef-462b-a220-8ae04237a56e",
        "timestamp": "2016-10-18 09:52:05.219414",
        "publisher_id": "infra-optim:node0"
      }

**actionplan.cancel.end**

.. code-block:: json

    {
      "event_type": "action_plan.execution.end",
      "payload": {
        "watcher_object.namespace": "watcher",
        "watcher_object.name": "ActionPlanCancelPayload",
        "watcher_object.version": "1.0",
        "watcher_object.data": {
          "created_at": "2016-10-18T09:52:05Z",
          "deleted_at": null,
          "audit_uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
          "audit": {
            "watcher_object.namespace": "watcher",
            "watcher_object.name": "TerseAuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.data": {
              "created_at": "2016-10-18T09:52:05Z",
              "deleted_at": null,
              "uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "scope": [],
              "audit_type": "ONESHOT",
              "state": "SUCCEEDED",
              "parameters": {},
              "interval": null,
              "updated_at": null
            }
          },
          "uuid": "76be87bd-3422-43f9-93a0-e85a577e3061",
          "fault": null,
          "state": "CANCELLED",
          "global_efficacy": {},
          "strategy_uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
          "strategy": {
            "watcher_object.namespace": "watcher",
            "watcher_object.name": "StrategyPayload",
            "watcher_object.version": "1.0",
            "watcher_object.data": {
              "created_at": "2016-10-18T09:52:05Z",
              "deleted_at": null,
              "name": "TEST",
              "uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
              "parameters_spec": {},
              "display_name": "test strategy",
              "updated_at": null
            }
          },
          "updated_at": null
        }
      },
      "priority": "INFO",
      "message_id": "3984dc2b-8aef-462b-a220-8ae04237a56e",
      "timestamp": "2016-10-18 09:52:05.219414",
      "publisher_id": "infra-optim:node0"
    }

**actionplan.cancel.error**

.. code-block:: json

    {
      "event_type": "action_plan.cancel.error",
      "publisher_id": "infra-optim:node0",
      "priority": "ERROR",
      "message_id": "9a45c5ae-0e21-4300-8fa0-5555d52a66d9",
      "payload": {
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher",
        "watcher_object.name": "ActionPlanCancelPayload",
        "watcher_object.data": {
          "fault": {
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher",
            "watcher_object.name": "ExceptionPayload",
            "watcher_object.data": {
            "exception_message": "TEST",
            "module_name": "watcher.tests.notifications.test_action_plan_notification",
            "function_name": "test_send_action_plan_cancel_with_error",
            "exception": "WatcherException"
          }
        },
        "uuid": "76be87bd-3422-43f9-93a0-e85a577e3061",
        "created_at": "2016-10-18T09:52:05Z",
        "strategy_uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
        "strategy": {
          "watcher_object.version": "1.0",
          "watcher_object.namespace": "watcher",
          "watcher_object.name": "StrategyPayload",
          "watcher_object.data": {
            "uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
            "created_at": "2016-10-18T09:52:05Z",
            "name": "TEST",
            "updated_at": null,
            "display_name": "test strategy",
            "parameters_spec": {},
           "deleted_at": null
         }
       },
       "updated_at": null,
       "deleted_at": null,
       "audit_uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
       "audit": {
         "watcher_object.version": "1.0",
         "watcher_object.namespace": "watcher",
         "watcher_object.name": "TerseAuditPayload",
         "watcher_object.data": {
           "parameters": {},
           "uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
           "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
           "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
           "created_at": "2016-10-18T09:52:05Z",
           "scope": [],
           "updated_at": null,
           "audit_type": "ONESHOT",
           "interval": null,
           "deleted_at": null,
           "state": "SUCCEEDED"
         }
       },
       "global_efficacy": {},
       "state": "CANCELLING"
     }
   },
   "timestamp": "2016-10-18 09:52:05.219414"
 }

**action.cancel.start**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.namespace": "watcher",
        "watcher_object.version": "1.0",
        "watcher_object.name": "ActionCancelPayload",
        "watcher_object.data": {
          "uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
          "input_parameters": {
            "param2": 2,
            "param1": 1
          },
          "fault": null,
          "created_at": "2016-10-18T09:52:05Z",
          "updated_at": null,
          "state": "CANCELLING",
          "action_plan": {
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0",
            "watcher_object.name": "TerseActionPlanPayload",
            "watcher_object.data": {
              "uuid": "76be87bd-3422-43f9-93a0-e85a577e3061",
              "global_efficacy": {},
              "created_at": "2016-10-18T09:52:05Z",
              "updated_at": null,
              "state": "CANCELLING",
              "audit_uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
              "strategy_uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
              "deleted_at": null
            }
          },
          "parents": [],
          "action_type": "nop",
          "deleted_at": null
        }
      },
      "event_type": "action.cancel.start",
      "publisher_id": "infra-optim:node0",
      "timestamp": "2017-01-01 00:00:00.000000",
      "message_id": "530b409c-9b6b-459b-8f08-f93dbfeb4d41"
    }

**action.cancel.end**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.namespace": "watcher",
        "watcher_object.version": "1.0",
        "watcher_object.name": "ActionCancelPayload",
        "watcher_object.data": {
          "uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
          "input_parameters": {
            "param2": 2,
            "param1": 1
          },
          "fault": null,
          "created_at": "2016-10-18T09:52:05Z",
          "updated_at": null,
          "state": "CANCELLED",
          "action_plan": {
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0",
            "watcher_object.name": "TerseActionPlanPayload",
            "watcher_object.data": {
              "uuid": "76be87bd-3422-43f9-93a0-e85a577e3061",
              "global_efficacy": {},
              "created_at": "2016-10-18T09:52:05Z",
              "updated_at": null,
              "state": "CANCELLING",
              "audit_uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
              "strategy_uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
              "deleted_at": null
            }
          },
          "parents": [],
          "action_type": "nop",
          "deleted_at": null
        }
      },
      "event_type": "action.cancel.end",
      "publisher_id": "infra-optim:node0",
      "timestamp": "2017-01-01 00:00:00.000000",
      "message_id": "530b409c-9b6b-459b-8f08-f93dbfeb4d41"
    }

**action.cancel.error**

.. code-block:: json

    {
      "priority": "ERROR",
      "payload": {
        "watcher_object.namespace": "watcher",
        "watcher_object.version": "1.0",
        "watcher_object.name": "ActionCancelPayload",
        "watcher_object.data": {
          "uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
          "input_parameters": {
            "param2": 2,
            "param1": 1
          },
          "fault": {
          "watcher_object.namespace": "watcher",
          "watcher_object.version": "1.0",
          "watcher_object.name": "ExceptionPayload",
          "watcher_object.data": {
            "module_name": "watcher.tests.notifications.test_action_notification",
            "exception": "WatcherException",
            "exception_message": "TEST",
            "function_name": "test_send_action_cancel_with_error"
          }
        },
        "created_at": "2016-10-18T09:52:05Z",
        "updated_at": null,
        "state": "FAILED",
        "action_plan": {
          "watcher_object.namespace": "watcher",
          "watcher_object.version": "1.0",
          "watcher_object.name": "TerseActionPlanPayload",
          "watcher_object.data": {
            "uuid": "76be87bd-3422-43f9-93a0-e85a577e3061",
            "global_efficacy": {},
            "created_at": "2016-10-18T09:52:05Z",
            "updated_at": null,
            "state": "CANCELLING",
            "audit_uuid": "10a47dd1-4874-4298-91cf-eff046dbdb8d",
            "strategy_uuid": "cb3d0b58-4415-4d90-b75b-1e96878730e3",
            "deleted_at": null
          }
        },
        "parents": [],
        "action_type": "nop",
        "deleted_at": null
      }
    },
    "event_type": "action.cancel.error",
    "publisher_id": "infra-optim:node0",
    "timestamp": "2017-01-01 00:00:00.000000",
    "message_id": "530b409c-9b6b-459b-8f08-f93dbfeb4d41"
   }

Alternatives
------------

we can work with actionplan.update and action.update notification, but
**actionplan cancel**  is a complete operation not just status update so
defining new notifications is better approach.

Data model impact
-----------------

None.

REST API impact
---------------

None.

Security impact
---------------

None.

Notifications impact
--------------------

This blueprint will implement the following notifications:

- ``actionplan.cancel.start``
- ``actionplan.cancel.end``
- ``actionplan.cancel.error``
- ``action.cancel.start``
- ``action.cancel.end``
- ``action.cancel.error``

Other end user impact
---------------------

None.

Performance Impact
------------------

None.

Other deployer impact
---------------------

None.

Developer impact
----------------

None.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  adisky <aditi.s@nectechnologies.in>

Work Items
----------

Implement the Notfications as described in "Proposed change" section.

Dependencies
============

None.

Testing
=======

unit tests should be added for new notifications.

Documentation Impact
====================

A notification sample should be added in watcher documentation.

References
==========

.. _action plan: https://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _action: http://docs.openstack.org/developer/watcher/glossary.html#action
