..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================
Add Show Datamodel API
======================

https://blueprints.launchpad.net/watcher/+spec/show-datamodel-api


Problem description
===================

The datamodel is very important for Watcher to generate resource
optimization solutions. Currently, it can only be found by looking at
the log file, which is very inconvenient. Therefore, it is necessary
to add an api to facilitate the user to quickly view the datamodel.

Use Cases
----------

As a Watcher user, I want to use Show Datamodel API to
see the information of the instance in the specified scope.


Proposed change
===============

We can refer to the **"strategy list"** command, add the command line
interface in the python-watcherclient. After receiving the request,
the watcher-api calls watcher-decision-engine to retrieve the information
about the datamodel, then parses and returns.

The command line interface used in watcherclient could be like this:

* watcher datamodel list [--audit <audit_id>]

In watcherclient, we can add **"datamodel.py,datamodel_shell.py"** to send
datamodel list request and receive the result.

In watcher-api, we can add **"datamodel.py"** to recieve the
python-watcherclient's request and call watcher-decision-engine module.

In watcher-decision-engine, we can get datamodel data according to the
specified scope, then parses the datamodel and return to watcher-api.

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

Add following **datamodel** REST:

* GET /v1/datamodels

  * Normal http response code(200)
  * Expected error http response code(400,401)

* Request

  * **audit_uuid (Optional)**: UUID of an audit

* Response

  * **instance_uuid**: UUID of an instance
  * **node_uuid**: UUID of an compute node
  * **instance_state**: state of instance
  * **node_state**: state of compute node

* GET /v1/datamodels/detail

  * Normal http response code(200)
  * Expected error http response code(400,401)

* Request

  * **audit_uuid (Optional)**: UUID of an audit

* Response

  * **instance_uuid**: UUID of an instance
  * **instance_state**: state of instance
  * **instance_name**: name of instance
  * **instance_vcpus**: number of instance vcpus
  * **instance_memory**: memory of instance
  * **instance_disk**: disk of instance
  * **instance_disk_capacity**: disk capacity of instance
  * **node_uuid**: UUID of an compute node
  * **node_state**: state of compute node
  * **node_name**: name of node
  * **node_vcpus**: number of compute node vcpus
  * **node_memory**: memory of node
  * **node_disk**: disk of node
  * **node_disk_capacity**: disk capacity of node


* Example JSON representation of Datamodel

::

  {
    "compute": [
      {
        "node_uuid": "90d7da5c-d432-4eba-89b4-743c9f1e6cfa",
        "node_name": "node_1",
        "node_vcpus": 48,
        "node_memory": "4096",
        "node_disk": "40",
        "node_disk_capacity": "60"
        "servers": [
          {
            "instance_uuid": "9e7cbe91-b391-4394-a42c-68996a4fd555",
            "instance_state": "active",
            "instance_name": "vm_4",
            "instance_vcpus": 16,
            "instance_memory": "2048",
            "instance_disk": "10",
            "instance_disk_capacity": "35",
          },
          {
            "instance_uuid": "8e7cbe91-b391-4394-a42c-68996a4fd555",
            "instance_state": "active",
            "instance_name": "vm_5",
            "instance_vcpus": 16,
            "instance_memory": "2048",
            "instance_disk": "10",
            "instance_disk_capacity": "35",
          }
        ]
      },
      {
        "node_uuid": "78d7da5c-d432-4eba-89b4-743c9f1e6cfa",
        "node_name": "node_2",
        "node_vcpus": 96,
        "node_memory": "4096",
        "node_disk": "60",
        "node_disk_capacity": "60"
        "servers": [
          {
            "instance_uuid": "6b7cbe91-b391-4394-a42c-68996a4fd55b",
            "instance_state": "active",
            "instance_name": "vm_1",
            "instance_vcpus": 32,
            "instance_memory": "2048",
            "instance_disk": "10",
            "instance_disk_capacity": "35",
          },
          {
            "instance_uuid": "527cbe91-b391-4394-a42c-68996a4fd5e7",
            "instance_state": "active",
            "instance_name": "vm_2",
            "instance_vcpus": 16,
            "instance_memory": "2048",
            "instance_disk": "10",
            "instance_disk_capacity": "35",
          }
        ]
      }
    ]
  }

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

The user can view the datamodel through the command below
in python-watcherclient:

* watcher datamodel list

and add the **audit** parameter to filter the datamodel in the
specified scope:

* watcher datamodel list [--audit <audit_id>]

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
  <chenker>

Other contributors:
  <li-canwei2> , <yumeng-bao>

Work Items
----------

- Add **watcher datamodel list** command line interface
  in watcherclient.

- Add verification and processing of request from
  watcherclient in watcher-api.

- Add parsing, encapsulation, and return of datamodel
  in watcher-decision-engine.


Dependencies
============

None


Testing
=======

Unit test on the watcher-decision-engine, python-watcherclient, watcher-api.


Documentation Impact
====================

* A documentation explaining how to use
  **watcher datamodel list [--audit <audit_id>]**

* Update API Reference

* Update REST API Version History


References
==========

None


History
=======

None
