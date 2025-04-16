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

The data model is very important for Watcher to generate resource
optimization solutions. Currently, it can only be found by looking at
the log file, which is very inconvenient. Therefore, it is necessary
to add an api to facilitate the user to quickly view the current datamodel
in memory.

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

* openstack optimize datamodel list [--audit <audit_uuid>]
* [--type <type>] [--detail]

In watcherclient, we can add **"data_model.py,data_model_shell.py"** to send
datamodel list request and receive the result.

In watcher-api, we can add **"data_model.py"** to recieve the
python-watcherclient's request and call watcher-decision-engine module.

In watcher-decision-engine, we can get datamodel data according to the
specified scope and the type, then parses the datamodel and return to
watcher-api.

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

Add following **data model** REST:

* GET /v1/data_model

  * Normal http response code(200)
  * Expected error http response code(400,401)

* Request

  * **audit_uuid (Optional)**: UUID of an audit
  * **type (Optional)**: Type of data model user want to list

* Response

  * **server_uuid**: UUID of server
  * **server_name**: name of server
  * **server_vcpus**: number of server vcpus
  * **server_memory**: memory of server
  * **server_disk**: disk of server
  * **server_state**: state of server
  * **node_uuid**: UUID of node
  * **node_hostname**: name of node
  * **node_vcpus**: number of node vcpus
  * **node_vcpu_ratio**: vcpu ratio of node
  * **node_memory**: memory of node
  * **node_memory_ratio**: memory ratio of node
  * **node_disk**: disk of node
  * **node_disk_ratio**: disk ratio of node
  * **node_state**: state of node


* Example JSON representation of compute data model

::

  {
      "context": [
          {
              "server_uuid": "1bf91464-9b41-428d-a11e-af691e5563bb",
              "server_name": "chenke-test1",
              "server_vcpus": "1",
              "server_memory": "512",
              "server_disk": "1",
              "server_state": "active",
              "node_uuid": "253e5dd0-9384-41ab-af13-4f2c2ce26112",
              "node_hostname": "localhost.localdomain",
              "node_vcpus": "4",
              "node_vcpu_ratio": "16.0",
              "node_memory": "16383",
              "node_memory_ratio": "1.5",
              "node_disk": "37"
              "node_disk_ratio": "1.0",
              "node_state": "up",
          },
          {
              "server_uuid": "e2cb5f6f-fa1d-4ba2-be1e-0bf02fa86ba4",
              "server_name": "chenke-test2",
              "server_vcpus": "1",
              "server_memory": "512",
              "server_disk": "1",
              "server_state": "active",
              "node_uuid": "253e5dd0-9384-41ab-af13-4f2c2ce26112",
              "node_hostname": "localhost.localdomain",
              "node_vcpus": "4",
              "node_vcpu_ratio": "16.0",
              "node_memory": "16383",
              "node_memory_ratio": "1.5",
              "node_disk": "37"
              "node_disk_ratio": "1.0",
              "node_state": "up",
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

* watcher datamodel list [--audit <audit_uuid>]

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
  **watcher datamodel list [--audit <audit_uuid>] [--type <type>] [--detail]**

* Update API Reference

* Update REST API Version History


References
==========

None


History
=======


.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Stein
     - Introduced
   * - Train
     - Updated

