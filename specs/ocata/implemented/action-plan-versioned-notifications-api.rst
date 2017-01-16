..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================================
Versioned notifications for action plans
========================================

https://blueprints.launchpad.net/watcher/+spec/action-plan-versioned-notifications-api

Following the implementation of the `watcher-notifications-ovo blueprint`_,
Watcher now has all the necessary prerequisites in order to provide versioned
notifications throughout its codebase. This blueprint will focus on describing
the notifications to implement in Watcher concerning the `Action Plan`_ object.

Problem description
===================

As of now, there is no way for any service (Watcher included) to know when an
action plan has been created, modified or deleted. This prevents any form of
event-based reaction which may be useful for 3rd party services or plugins.

Use Cases
---------

As an OpenStack developer, I want to be able to listen to notifications coming
from Watcher about action plans.

As an OpenStack developer, I want to know what the format of the action plan
notifications are.

As an OpenStack developer, I want to be notified whenever:

- an action plan has been created, updated or deleted
- an action plan has finished

As an OpenStack developer, I would also want to be notified whenever:

- the action plan starts the execution of its actions (the action plan is
  triggered by the `Applier`_)
- the action plan finishes its execution
- the action plan fails with error


Proposed change
===============

In order to implement the above use cases, many different notifications will
be needed:

- ``actionplan.create`` whenever an action plan has been created.
- ``actionplan.update`` whenever an action plan has been updated. This includes
  all state updates including the deletion of the action plan.
- ``actionplan.delete`` whenever an action plan has been deleted (soft).
- ``actionplan.execution.start`` whenever an action plan starts.
- ``actionplan.execution.end`` whenever an action plan ends.
- ``actionplan.execution.error`` whenever an action plan fails.

Moreover, we will rely on `oslo.versionedobjects`_ to version the payloads of
action plan-related notifications.

Here below is suggestion of notification structure for each one of the
aforementioned events:

**actionplan.create**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6",
          "state": "RECOMMENDED",
          "global_efficacy": {
              "description": "Global efficacy",
              "name": "test_global_efficacy",
              "unit": "%",
              "value": 95
          },
          "audit_uuid": "55bc1fe8-8030-4bd0-b0d0-2e62937f02a0",
          "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
          "updated_at": null,
          "deleted_at": null,
          "created_at": "2016-11-04T16:29:20Z",
          "audit": {
            "watcher_object.data": {
              "audit_type": "ONESHOT",
              "parameters": {
                "para2": "hello",
                "para1": 3.2
              },
              "state": "SUCCEEDED",
              "updated_at": null,
              "deleted_at": null,
              "fault": null,
              "interval": null,
              "scope": [],
              "created_at": "2016-11-04T16:29:20Z",
              "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6"
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
            },
            "watcher_object.name": "AuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "strategy": {
            "watcher_object.data": {
              "parameters_spec": {
                "properties": {
                  "para2": {
                    "type": "string",
                    "default": "hello",
                    "description": "string parameter example"
                  },
                  "para1": {
                    "description": "number parameter example",
                    "maximum": 10.2,
                    "type": "number",
                    "default": 3.2,
                    "minimum": 1.0
                  }
                }
              },
              "name": "dummy",
              "uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "updated_at": null,
              "deleted_at": null,
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy strategy"
            },
            "watcher_object.name": "StrategyPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          }
        },
        "watcher_object.name": "ActionPlanCreatePayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673",
      "event_type": "actionplan.create",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**actionplan.update**

.. code-block:: json

    {
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:51:38.722986",
      "payload": {
        "watcher_object.name": "ActionPlanUpdatePayload",
        "watcher_object.data": {
          "global_efficacy": {
              "description": "Global efficacy",
              "name": "test_global_efficacy",
              "unit": "%",
              "value": 95
          },
          "strategy": {
            "watcher_object.name": "StrategyPayload",
            "watcher_object.data": {
              "name": "dummy",
              "parameters_spec": {
                "properties": {
                  "para2": {
                    "default": "hello",
                    "type": "string",
                    "description": "string parameter example"
                  },
                  "para1": {
                    "maximum": 10.2,
                    "default": 3.2,
                    "minimum": 1.0,
                    "description": "number parameter example",
                    "type": "number"
                  }
                }
              },
              "updated_at": null,
              "display_name": "Dummy strategy",
              "deleted_at": null,
              "uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "audit_uuid": "55bc1fe8-8030-4bd0-b0d0-2e62937f02a0",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "created_at": "2016-11-04T16:25:35Z"
            },
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "audit": {
            "watcher_object.data": {
              "audit_type": "ONESHOT",
              "parameters": {
                "para2": "hello",
                "para1": 3.2
              },
              "state": "SUCCEEDED",
              "updated_at": null,
              "deleted_at": null,
              "fault": null,
              "interval": null,
              "scope": [],
              "created_at": "2016-11-04T16:29:20Z",
              "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6"
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
            },
            "watcher_object.name": "AuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "created_at": "2016-11-04T16:51:21Z",
          "uuid": "f1e0d912-afd9-4bf2-91ef-c99cd08cc1ef",
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "deleted_at": null,
          "state_update": {
            "watcher_object.name": "ActionPlanStateUpdatePayload",
            "watcher_object.data": {
              "state": "ONGOING",
              "old_state": "PENDING"
            },
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "state": "ONGOING",
          "priority": "INFO",
          "event_type": "actionplan.update",
          "message_id": "697fdf55-7252-4b6c-a2c2-5b9e85f6342c"
        }
     }
  }

**actionplan.delete**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6",
          "state": "DELETED",
          "global_efficacy": {
              "description": "Global efficacy",
              "name": "test_global_efficacy",
              "unit": "%",
              "value": 95
          },
          "audit_uuid": "55bc1fe8-8030-4bd0-b0d0-2e62937f02a0",
          "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
          "updated_at": null,
          "deleted_at": null,
          "created_at": "2016-11-04T16:29:20Z",
          "audit": {
            "watcher_object.data": {
              "audit_type": "ONESHOT",
              "parameters": {
                "para2": "hello",
                "para1": 3.2
              },
              "state": "SUCCEEDED",
              "updated_at": null,
              "deleted_at": null,
              "fault": null,
              "interval": null,
              "scope": [],
              "created_at": "2016-11-04T16:29:20Z",
              "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6"
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
            },
            "watcher_object.name": "AuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "strategy": {
            "watcher_object.data": {
              "parameters_spec": {
                "properties": {
                  "para2": {
                    "type": "string",
                    "default": "hello",
                    "description": "string parameter example"
                  },
                  "para1": {
                    "description": "number parameter example",
                    "maximum": 10.2,
                    "type": "number",
                    "default": 3.2,
                    "minimum": 1.0
                  }
                }
              },
              "name": "dummy",
              "uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "updated_at": null,
              "deleted_at": null,
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy strategy"
            },
            "watcher_object.name": "StrategyPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          }
        },
        "watcher_object.name": "ActionPlanDeletePayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673",
      "event_type": "actionplan.delete",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**actionplan.execution.start**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6",
          "state": "PENDING",
          "global_efficacy": {
              "description": "Global efficacy",
              "name": "test_global_efficacy",
              "unit": "%",
              "value": 95
          },
          "audit_uuid": "55bc1fe8-8030-4bd0-b0d0-2e62937f02a0",
          "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
          "updated_at": null,
          "deleted_at": null,
          "created_at": "2016-11-04T16:29:20Z",
          "audit": {
            "watcher_object.data": {
              "audit_type": "ONESHOT",
              "parameters": {
                "para2": "hello",
                "para1": 3.2
              },
              "state": "SUCCEEDED",
              "updated_at": null,
              "deleted_at": null,
              "fault": null,
              "interval": null,
              "scope": [],
              "created_at": "2016-11-04T16:29:20Z",
              "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6"
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
            },
            "watcher_object.name": "AuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "strategy": {
            "watcher_object.data": {
              "parameters_spec": {
                "properties": {
                  "para2": {
                    "type": "string",
                    "default": "hello",
                    "description": "string parameter example"
                  },
                  "para1": {
                    "description": "number parameter example",
                    "maximum": 10.2,
                    "type": "number",
                    "default": 3.2,
                    "minimum": 1.0
                  }
                }
              },
              "name": "dummy",
              "uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "updated_at": null,
              "deleted_at": null,
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy strategy"
            },
            "watcher_object.name": "StrategyPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          }
        },
        "watcher_object.name": "ActionPlanActionPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673",
      "event_type": "actionplan.execution.start",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**actionplan.execution.end**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6",
          "state": "SUCCEEDED",
          "global_efficacy": {
              "description": "Global efficacy",
              "name": "test_global_efficacy",
              "unit": "%",
              "value": 95
          },
          "audit_uuid": "55bc1fe8-8030-4bd0-b0d0-2e62937f02a0",
          "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
          "updated_at": null,
          "deleted_at": null,
          "created_at": "2016-11-04T16:29:20Z",
          "audit": {
            "watcher_object.data": {
              "audit_type": "ONESHOT",
              "parameters": {
                "para2": "hello",
                "para1": 3.2
              },
              "state": "SUCCEEDED",
              "updated_at": null,
              "deleted_at": null,
              "fault": null,
              "interval": null,
              "scope": [],
              "created_at": "2016-11-04T16:29:20Z",
              "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6",
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39"
            },
            "watcher_object.name": "AuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "strategy": {
            "watcher_object.data": {
              "parameters_spec": {
                "properties": {
                  "para2": {
                    "type": "string",
                    "default": "hello",
                    "description": "string parameter example"
                  },
                  "para1": {
                    "description": "number parameter example",
                    "maximum": 10.2,
                    "type": "number",
                    "default": 3.2,
                    "minimum": 1.0
                  }
                }
              },
              "name": "dummy",
              "uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "updated_at": null,
              "deleted_at": null,
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy strategy"
            },
            "watcher_object.name": "StrategyPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          }
        },
        "watcher_object.name": "ActionPlanActionPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673",
      "event_type": "actionplan.execution.end",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**actionplan.execution.error**

.. code-block:: json

    {
      "priority": "ERROR",
      "payload": {
        "watcher_object.data": {
          "state": "ONGOING",
          "updated_at": null,
          "deleted_at": null,
          "audit_uuid": "55bc1fe8-8030-4bd0-b0d0-2e62937f02a0",
          "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a3",
          "global_efficacy": {
              "description": "Global efficacy",
              "name": "test_global_efficacy",
              "unit": "%",
              "value": 95
          },
          "fault": {
            "watcher_object.data": {
              "exception": "WatcherException",
              "exception_message": "TEST",
              "function_name": "test_send_action_plan_action_with_error",
              "module_name": "watcher.tests.notifications.test_action_plan_notification"
            },
            "watcher_object.name": "ExceptionPayload",
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "audit": {
            "watcher_object.data": {
              "audit_type": "ONESHOT",
              "parameters": {
                "para2": "hello",
                "para1": 3.2
              },
              "state": "SUCCEEDED",
              "updated_at": null,
              "deleted_at": null,
              "fault": null,
              "interval": null,
              "scope": [],
              "created_at": "2016-11-04T16:29:20Z",
              "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6",
              "goal_uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "strategy_uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39"
            },
            "watcher_object.name": "AuditPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "strategy": {
            "watcher_object.data": {
              "parameters_spec": {
                "properties": {
                  "para2": {
                    "type": "string",
                    "default": "hello",
                    "description": "string parameter example"
                  },
                  "para1": {
                    "description": "number parameter example",
                    "maximum": 10.2,
                    "type": "number",
                    "default": 3.2,
                    "minimum": 1.0
                  }
                }
              },
              "name": "dummy",
              "uuid": "75234dfe-87e3-4f11-a0e0-3c3305d86a39",
              "updated_at": null,
              "deleted_at": null,
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy strategy"
            },
            "watcher_object.name": "StrategyPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "created_at": "2016-11-04T16:29:20Z",
          "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6"
        },
        "watcher_object.name": "ActionPlanActionPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673",
      "event_type": "actionplan.execution.error",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

Alternatives
------------

Instead of using versioned objects, we can define the payload of our action
plan notifications without any support for versioning.

Data model impact
-----------------

New versioned objects will be created although none of them are to be persisted
as they will be used to structure the content of the notifications.

Here are some of the payloads to be declared:

.. code-block:: python

    @base.WatcherObjectRegistry.register_notification
    class ActionPlanPayload(base.NotificationPayloadBase):

        VERSION = '1.0'

        fields = {
            'uuid': fields.UUIDField(),
            'state': fields.StringField(),
            'global_efficacy': fields.FlexibleDictField(nullable=True),
            'audit_uuid': fields.UUIDField(),
            'audit': fields.ObjectField('Audit'),
            'strategy_uuid': fields.UUIDField(nullable=True),
            'strategy': fields.ObjectField('Strategy', nullable=True),
            'created_at': fields.DateTimeField(nullable=True),
            'updated_at': fields.DateTimeField(nullable=True),
            'deleted_at': fields.DateTimeField(nullable=True),
        }


    @base.WatcherObjectRegistry.register_notification
    class ActionPlanStateUpdatePayload(base.NotificationPayloadBase):

        VERSION = '1.0'

        fields = {
            'old_state': fields.StringField(nullable=True),
            'state': fields.StringField(nullable=True),
        }


    @base.WatcherObjectRegistry.register_notification
    class ActionPlanUpdatePayload(ActionPlanPayload):

        VERSION = '1.0'

        fields = {
            'state_update': fields.ObjectField('ActionPlanStateUpdatePayload'),
        }


REST API impact
---------------

None.

Security impact
---------------

None.

Notifications impact
--------------------

This blueprint will implement the following notifications:

- ``actionplan.create``
- ``actionplan.update``
- ``actionplan.delete``
- ``actionplan.execution.start``
- ``actionplan.execution.end``
- ``actionplan.execution.error``

Other end user impact
---------------------

None.

Performance Impact
------------------

When enabled, code to send the notification will be called each time an event
occurs that triggers a notification. This shouldn’t be much of a problem for
Watcher itself, but the load on whatever message bus is used should be
considered.

Other deployer impact
---------------------

In order for the notifications to be emitted, the deployer will have to
configure the notification topics using `oslo.messaging`_. Other configuration
options exposed via `oslo.messaging`_ may also be tuned.

Developer impact
----------------

Developers should adhere to proper versioning guidelines and use the
notification base classes when creating/updating notifications.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  vincent-francoise

Work Items
----------

- Implement ``actionplan.create``
- Implement ``actionplan.update``
- Implement ``actionplan.delete``
- Implement ``actionplan.execution.start``
- Implement ``actionplan.execution.end``
- Implement ``actionplan.execution.error``

Dependencies
============

- `watcher-versioned-objects`_
- `watcher-notifications-ovo`_

Testing
=======

These notifications will have to be tested mainly via unit testing.

Documentation Impact
====================

A notification sample should be provided and made dynamically available in the
online documentation.

The sequence diagrams in the `Watcher architecture`_.

References
==========

None.

.. _Action Plan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _watcher-notifications-ovo blueprint: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
.. _watcher-versioned-objects: https://blueprints.launchpad.net/watcher/+spec/watcher-versioned-objects
.. _watcher-notifications-ovo: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
.. _oslo.versionedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/
.. _configure the notification topics: http://docs.openstack.org/developer/oslo.messaging/opts.html#oslo-messaging-notifications
.. _oslo.messaging: http://docs.openstack.org/developer/oslo.messaging/
.. _Applier: http://docs.openstack.org/developer/watcher/glossary.html#watcher-applier-definition
.. _Watcher architecture: http://docs.openstack.org/developer/watcher/architecture.html#watcher-applier
.. _Watcher Planner: http://docs.openstack.org/developer/watcher/glossary.html#watcher-planner
