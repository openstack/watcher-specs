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


- Define a mapping of action_type and description

  + action_type: 'migrate'

    description: 'Moving a VM instance from source_node to destination_node'

  + action_type: 'change_nova_service_state'

    description: 'Disables or enables the nova-compute service.
                  A disabled nova-compute service can not be selected
                  by the nova for future deployment of new server.'

  + action_type: 'resize'

    description: 'Resize a server with specified flavor.'

  + action_type: 'sleep'

    description: 'Wait for a given interval in seconds.'

  + action_type: 'nop'

    description: 'Logging a NOP message'


- Add a new table to save the mapping

  + This table includes action_type and action description.


- Show description of a specified action

  + Add the logic of computing action_description to "get_one" method in
    watcher/api/controllers/v1/action.py

Alternatives
------------

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
      "payload": {
        "watcher_object.namespace": "watcher",
        "watcher_object.version": "1.0",
        "watcher_object.name": "ActionInfoPayload",
        "watcher_object.data": {
          "description": "moving a VM instance",
          "action_type": "migrate",
        },
      },
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
        "watcher_object.namespace": "watcher"
        "watcher_object.version": "1.0",
        "watcher_object.name": "ActionInfoPayload",
        "watcher_object.data": {
          "action_type": "migrate",
          "description": "moving a VM instance",
        },
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2017-01-04 16:31:36.264673",
      "event_type": "action_info.emit",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

The implementation is as follows:
https://review.opendev.org/#/c/454638/
But in my test, The number of received notifications is often less than
the number of notifications sent.

Data model impact
-----------------

Add a new table named 'action_descriptions'.
This table includes action_type and action description.

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
  licanwei, hanrong

Work Items
----------
Add a new table to save the mapping
Add logic to update the table when action loading
Add logic to show the action description

Dependencies
============
None

Testing
=======

Unit tests should be updated.


Documentation Impact
====================

The documentation will have to be updated, especially the glossary, in order to
explain the new concepts regarding "action" definition.


References
==========

https://docs.openstack.org/watcher/latest/#action
https://docs.openstack.org/watcher/latest/#action-plan

History
=======

None
