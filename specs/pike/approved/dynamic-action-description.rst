..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=======================================
Support Description For Dynamic Action
=======================================

https://blueprints.launchpad.net/watcher/+spec/dynamic-action-description

Add description property for dynamic action. Admin can see detail information
of any specify action.


Problem description
===================
Currently, a cloud admin has no way to see the description of planned actions
before running an action plan. This literal description is important when the
cloud admin wants to see detailed information about a recommended action plan.

Use Cases
---------

As a cloud administrator, I want to be able to see the description of
planned actions before running an action plan.

Proposed change
===============

Allow RESTful API(GET /v1/actions/(action_uuid)) to get description information
of a specified action.

Define different action-description templates for different action types.

Localize action-description.


Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

URLs with **/v1/actions/** and that uses the type **Action**:

* GET /v1/actions/(action_uuid)
* GET /v1/actions/detail

There will be a new action description field in the REST URLs
respond message.

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

Aside from the API, here are there other ways a user will interact with this
feature:

* impact on **python-watcherclient**:

  * Display the "description" field when displaying details about an action.


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
  hanrong

Work Items
----------

A literal description is computed from action type and parameters of an action.

- Implement 2 notifications:

  In order to share the description of all the action plugins installed
  alongside the Applier so that we wouldn't need to also install these plugins
  on the API side

  + the 1st one the API side that requests the action descriptions and the 2nd
    one on the Applier side that emits all the actions, including their
    descriptions (both notifications will have to be versioned).

  + The latter will also have to be emitted upon starting the Applier to notify
    the API of any change of description.

**action_info.request**

.. code-block:: json

    {
      "priority": "INFO",
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2017-01-04 16:31:36.264673",
      "event_type": "action_info.request",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }


**action_info.emit**

.. code-block:: json

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "action_type": "migrate",
          "description-template": "Migrates a server to a destination node"
        },
        "watcher_object.name": "ActionInfoPayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2017-01-04 16:31:36.264673",
      "event_type": "action_info.emit",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

- Define a mapping of action_type and description-template

  + acton_type: 'migrate'

    description_template: '%s migration of the instance %s from %s to %s' % (
                           migration_type, resource_id, source_node,
                           destination_node)

  + action_type: 'change_nova_service_state'

    description_template: 'Change the state of Nova service state to %s for %s'
                          % (state, resource_id)


- Show description of a specified action by computing from action_type and
  action_description_template dynamically.

  + Add the logic of computing action_description to "get_one" method in
    watcher/api/controllers/v1/action.py


Dependencies
============

https://blueprints.launchpad.net/watcher/+spec/
action-versioned-notifications-api


Testing
=======

None


Documentation Impact
====================

The documentation will have to be updated, especially the glossary, in order to
explain the new concepts regarding "action" definition.


References
==========

None


History
=======

None