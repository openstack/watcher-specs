..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Versioned notifications for actions
===================================

https://blueprints.launchpad.net/watcher/+spec/action-versioned-notifications-api

Following the implementation of the `watcher-notifications-ovo blueprint`_,
Watcher now has all the necessary prerequisites in order to provide versioned
notifications throughout its codebase. This blueprint will focus on describing
the notifications to implement in Watcher concerning the Action_ object.

Problem description
===================

As of now, there is no way for any service (Watcher included) to know when an
action has been created, modified or deleted. This prevents any form of
event-based reaction which may be useful for 3rd party services or plugins.

Use Cases
---------

As an OpenStack developer, I want to be able to listen to notifications coming
from Watcher about actions.

As an OpenStack developer, I want to know what the format of the action
notifications are.

As an OpenStack developer, I want to be notified whenever:

- an action has been created
- an action is updated
- an action has been deleted

As an OpenStack developer, I would also want to be notified whenever:

- an action starts its execution
- an action finishes its execution
- the execution of an action failed

Proposed change
===============

In order to implement the above use cases, many different notifications will
be needed:

- ``action.create`` whenever an action has been created.
- ``action.update`` whenever an action has been updated. This includes all
  state updates including the deletion of the action.
- ``action.delete`` whenever an action has been deleted (soft).
- ``action.execution.start`` whenever an action starts.
- ``action.execution.end`` whenever an action ends.
- ``action.execution.error`` whenever an action fails.

Moreover, we will rely on `oslo.versionedobjects`_ to version the payloads of
action-related notifications.

Here below is suggestion of notification structure for each one of the
aforementioned events:

**action.create**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "state": "PENDING",
          "updated_at": null,
          "deleted_at": null,
          "action_plan": {
            "watcher_object.data": {
              "uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "updated_at": null,
              "deleted_at": null,
              "created_at": "2016-11-04T16:25:35Z",
            },
            "watcher_object.name": "ActionPlanPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "interval": null,
          "scope": [],
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
        "watcher_object.name": "ActionCreatePayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673   ",
      "event_type": "action.create",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**action.update**

.. code-block:: json

    {
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:51:38.722986   ",
      "payload": {
        "watcher_object.name": "ActionUpdatePayload",
        "watcher_object.data": {
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
              "created_at": "2016-11-04T16:25:35Z"
            },
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "scope": [],
          "created_at": "2016-11-04T16:51:21Z",
          "uuid": "f1e0d912-afd9-4bf2-91ef-c99cd08cc1ef",
          "goal": {
            "watcher_object.name": "GoalPayload",
            "watcher_object.data": {
              "efficacy_specification": [],
              "updated_at": null,
              "name": "dummy",
              "display_name": "Dummy goal",
              "deleted_at": null,
              "uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "created_at": "2016-11-04T16:25:35Z"
            },
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "deleted_at": null,
          "state_update": {
            "watcher_object.name": "ActionStateUpdatePayload",
            "watcher_object.data": {
              "state": "ONGOING",
              "old_state": "PENDING"
            },
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "interval": null,
          "updated_at": null,
          "state": "ONGOING",
          "action_type": "NOP"
        },
        "watcher_object.namespace": "watcher",
        "watcher_object.version": "1.0"
      },
      "priority": "INFO",
      "event_type": "action.update",
      "message_id": "697fdf55-7252-4b6c-a2c2-5b9e85f6342c"
    }

**action.delete**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "action_type": "NOP",
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "state": "DELETED",
          "updated_at": null,
          "deleted_at": null,
          "goal": {
            "watcher_object.data": {
              "uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "name": "dummy",
              "updated_at": null,
              "deleted_at": null,
              "efficacy_specification": [],
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy goal"
            },
            "watcher_object.name": "GoalPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "interval": null,
          "scope": [],
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
        "watcher_object.name": "ActionDeletePayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673   ",
      "event_type": "action.delete",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**action.execution.start**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "action_type": "NOP",
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "state": "ONGOING",
          "updated_at": null,
          "deleted_at": null,
          "fault": null,
          "goal": {
            "watcher_object.data": {
              "uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "name": "dummy",
              "updated_at": null,
              "deleted_at": null,
              "efficacy_specification": [],
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy goal"
            },
            "watcher_object.name": "GoalPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "interval": null,
          "scope": [],
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
        "watcher_object.name": "ActionActionPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673   ",
      "event_type": "action.execution.start",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**action.execution.end**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "action_type": "NOP",
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "state": "ONGOING",
          "updated_at": null,
          "deleted_at": null,
          "fault": null,
          "goal": {
            "watcher_object.data": {
              "uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "name": "dummy",
              "updated_at": null,
              "deleted_at": null,
              "efficacy_specification": [],
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy goal"
            },
            "watcher_object.name": "GoalPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "interval": null,
          "scope": [],
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
        "watcher_object.name": "ActionActionPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673   ",
      "event_type": "action.execution.end",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

**action.execution.error**

.. code-block:: json

    {
      "priority": "ERROR",
      "payload": {
        "watcher_object.data": {
          "action_type": "NOP",
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "state": "ONGOING",
          "updated_at": null,
          "deleted_at": null,
          "fault": {
            "watcher_object.data": {
              "exception": "WatcherException",
              "exception_message": "TEST",
              "function_name": "test_send_action_action_with_error",
              "module_name": "watcher.tests.notifications.test_action_notification"
            },
            "watcher_object.name": "ExceptionPayload",
            "watcher_object.namespace": "watcher",
            "watcher_object.version": "1.0"
          },
          "goal": {
            "watcher_object.data": {
              "uuid": "bc830f84-8ae3-4fc6-8bc6-e3dd15e8b49a",
              "name": "dummy",
              "updated_at": null,
              "deleted_at": null,
              "efficacy_specification": [],
              "created_at": "2016-11-04T16:25:35Z",
              "display_name": "Dummy goal"
            },
            "watcher_object.name": "GoalPayload",
            "watcher_object.version": "1.0",
            "watcher_object.namespace": "watcher"
          },
          "interval": null,
          "scope": [],
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
        "watcher_object.name": "ActionActionPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673   ",
      "event_type": "action.execution.error",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

Alternatives
------------

Instead of using versioned objects, we can define the payload of our action
notifications without any support for versioning.

Data model impact
-----------------

New versioned objects will be created although none of them are to be persisted
as they will be used to structure the content of the notifications.

Here are some of the payloads to be declared:

.. code-block:: python

    @base.WatcherObjectRegistry.register_notification
    class ActionPayload(notificationbase.NotificationPayloadBase):

        VERSION = '1.0'

        fields = {
            'uuid': fields.UUIDField(),
            'action_type': fields.StringField(),
            'state': fields.StringField(),
            'parameters': fields.FlexibleDictField(nullable=True),
            'interval': fields.IntegerField(nullable=True),
            'goal_uuid': fields.UUIDField(),
            'strategy_uuid': fields.UUIDField(nullable=True),
            'goal': fields.ObjectField('Goal'),
            'strategy': fields.ObjectField('Strategy', nullable=True),
            'created_at': fields.DateTimeField(nullable=True),
            'updated_at': fields.DateTimeField(nullable=True),
            'deleted_at': fields.DateTimeField(nullable=True),
        }


    @base.WatcherObjectRegistry.register_notification
    class ActionStateUpdatePayload(notificationbase.NotificationPayloadBase):

        VERSION = '1.0'

        fields = {
            'old_state': fields.StringField(nullable=True),
            'state': fields.StringField(nullable=True),
        }


    @base.WatcherObjectRegistry.register_notification
    class ActionUpdatePayload(ActionPayload):

        VERSION = '1.0'

        fields = {
            'state_update': fields.ObjectField('ActionStateUpdatePayload'),
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

- ``action.create``
- ``action.update``
- ``action.delete``
- ``action.execution.start``
- ``action.execution.end``
- ``action.execution.error``

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
  joker946 <a.chadin@servionica.ru>

Work Items
----------

- Implement ``action.create``
- Implement ``action.update``
- Implement ``action.delete``
- Implement ``action.execution.start``
- Implement ``action.execution.end``
- Implement ``action.execution.error``

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

.. _Action: http://docs.openstack.org/developer/watcher/glossary.html#action
.. _watcher-notifications-ovo blueprint: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
.. _watcher-versioned-objects: https://blueprints.launchpad.net/watcher/+spec/watcher-versioned-objects
.. _watcher-notifications-ovo: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
.. _oslo.versionedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/
.. _configure the notification topics: http://docs.openstack.org/developer/oslo.messaging/opts.html#oslo-messaging-notifications
.. _oslo.messaging: http://docs.openstack.org/developer/oslo.messaging/
.. _Applier: http://docs.openstack.org/developer/watcher/glossary.html#watcher-applier-definition
.. _Watcher architecture: http://docs.openstack.org/developer/watcher/architecture.html#watcher-applier
