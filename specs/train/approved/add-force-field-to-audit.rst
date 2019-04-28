..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================
Add force field to Audit
========================

https://blueprints.launchpad.net/watcher/+spec/add-force-field-to-audit


Problem description
===================

As now, Watcher doesn't allow to launch a new audit when there
is actionplan ongoing. This is because if the new audit has
the same data model as the ongoing actionplan, the new audit
may create a wrong actionplan. But if there are different data
model scope, we should allow the new audit to run.

Use Cases
----------

As a Watcher user, I want to launch audit despite of ongoing actionplan.


Proposed change
===============

We need to add a new field **force** in audit table. If **force** is True,
Watcher will execute the audit even other actionplan is ongoing.

.. code-block:: python

    def pre_execute(self, audit, request_context):
        LOG.debug("Trigger audit %s", audit.uuid)
        if audit.force is False:
            self.check_ongoing_action_plans(request_context)
        # Write hostname that will execute this audit.
        audit.hostname = CONF.host
        # change state of the audit to ONGOING
        self.update_audit_state(audit, objects.audit.State.ONGOING)

The default value is False.
We also need to add an option in the post audit API. So that User can set
the value of the **force** field.
CLI example for creating audit with force:

.. code-block:: bash

   $ watcher audit create -g dummy --force


Alternatives
------------

None

Data model impact
-----------------

Add new **force** field in the audit table

REST API impact
---------------

Need to add new **force** parameter in Audits APIs.

Security impact
---------------

None

Notifications impact
--------------------

Add **force** to AuditPayload

**audit.create**

.. code-block:: python

    {
      "priority": "INFO",
      "payload": {
        "watcher_object.data": {
          "audit_type": "ONESHOT",
          "parameters": {
            "para2": "hello",
            "para1": 3.2
          },
          "state": "PENDING",
          "updated_at": null,
          "deleted_at": null,
          "interval": null,
          "scope": [],
          "force": False,
          "created_at": "2016-11-04T16:29:20Z",
          "uuid": "4a97b9dd-2023-43dc-b713-815bdd94d4d6"
         },
        "watcher_object.name": "AuditCreatePayload",
        "watcher_object.version": "1.0",
        "watcher_object.namespace": "watcher"
      },
      "publisher_id": "infra-optim:localhost",
      "timestamp": "2016-11-04 16:31:36.264673   ",
      "event_type": "audit.create",
      "message_id": "cbcf9f2c-7c53-4b4d-91ec-db49cca024b6"
    }

Other end user impact
---------------------

* Need to add **force** to CLI 'watcher audit create'
* Also need to update watcher-dashboard

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
  licanwei

Work Items
----------

* Update architecture doc to add the new field
* Add new **force** field in the audit table
* Check the value of **force** before running audit
* Update Watcher API version
* Update notification AuditPayload
* Update python-watcherclient
* Update watcher-dashboard


Dependencies
============

None


Testing
=======

Unittest for all changes


Documentation Impact
====================

Update architecture doc to add the new field.


References
==========

None


History
=======


.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced

