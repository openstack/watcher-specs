..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================
build baremetal data model in watcher
=====================================


https://blueprints.launchpad.net/watcher/+spec/build-baremetal-data-model-in-watcher

For a data center with large amount of VMs and physical hosts,the total power
consumption is tremendous. When workload is not heavy, Watcher can be used to
reduce power consumption by triggering a request to power off some idle hosts
without VMs. And when the workload increases Watcher will trigger a "power on"
request to fulfill the service requirements.

This "energy saving" goal can be fulfilled by adding four features in Watcher:
1) Build a new baremetal data model within current Watcher Cluster
Data Model
2) Add new actions "power on" and "power off" in Watcher
3) Implement a new strategy based on 'baremetal' and 'compute' data models,
which could trigger 'compute' and 'baremetal' actions.
4) Update the bare metal data model by ironic notifications

This spec implements the first feature: Build a new baremetal (ironic)
data model independent from current Watcher Cluster Data Model.

Problem description
===================

In the "power on" and "power off" actions, Watcher sends request to
power on/off physical machines managed by nova using ironic (ironic
calling IPMI tools). So watcher should know the hypervisor_id and node_uuid
of the target host(s), as well as their mapping list. In this spec,
we will build a baremetal data model in watcher to describe this mapping
list between hypervisor_id and node_uuid

Let's take an example, if we need to power off host 3 and 4 as shown in the
following list. But watcher doesn't know their node_uuid.


[root@host_192_51_151_2 ~(keystone_admin)]# nova hypervisor-list
+----+---------------------+-------+---------+
| ID | Hypervisor hostname | State | Status  |
+----+---------------------+-------+---------+
| 3  | host_192_51_151_3   | up    | enabled |
| 4  | host_192_51_151_5   | up    | enabled |
| 5  | host_192_51_151_7   | up    | enabled |
| 7  | host_192_51_151_8   | up    | enabled |
| 9  | host_192_51_151_9   | up    | enabled |
| 11 | host_192_51_151_10  | up    | enabled |
+----+---------------------+-------+---------+

So we establish a mapping list between hypervisor_id and
node_uuid. Just like the following:
+----+---------------------+--------------------------------------+---------+
| ID | Hypervisor hostname |              node_uuid               |  Extra  |
+----+---------------------+--------------------------------------+---------+
| 3  | host_192_51_151_3   | 4f37180e-c310-4327-a286-d5ab9ffc6497 |         |
| 4  | host_192_51_151_5   | 4f37180e-c310-4327-a286-d5ab9ffc6498 |         |
| 5  | host_192_51_151_7   | 4f37180e-c310-4327-a286-d5ab9ffc6499 |         |
| 7  | host_192_51_151_8   | 4f37180e-c310-4327-a286-d5ab9ffc6500 |         |
| 9  | host_192_51_151_9   | 4f37180e-c310-4327-a286-d5ab9ffc6501 |         |
| 11 | host_192_51_151_10  | 4f37180e-c310-4327-a286-d5ab9ffc6502 |         |
+----+---------------------+--------------------------------------+---------+

The "Extra" field is served as an extensible field.

Above all, from a watcher user's perspective, the whole procedure starts from
getting compute.node.id by 'nova hypervisor-list', then create ironic node
manually using 'ironic node create' as described in the proposed change part.
In the second step, the ironic_node_id is generated and the correlation is
built. Given all these id and correlation information, now we can create a
"power on and off" audit in watcher to do the optimization.

Use Cases
---------

As a developer, I want to have a new baremetal data model independant
from compute CDM in watcher to get the mapping list between
hypervisor_id and ironic node_uuid.

Proposed change
===============

1) Add "compute.node.id" info into Ironic node "extra" field when
   create nodes or update nodes info. Just like the following two ways:

* If we can not get compute.node.id before creating ironic node.
  1) ironic node-create
  2) nova hypervisor-list
  3) ironic node-update

* If we can get compute.node.id before creating ironic node.
  1) nova hypervisor-list
  2) ironic node-create

ironic node-create [-c <chassis>]
                   -d <driver>
                   [-i <key=value>]
                   [-p <key=value>]
                   [-e <key=value>]
                   [-u <uuid>]
                   [-n <name>]
                   [--network-interface <network_interface>]
                   [--resource-class <resource_class>]
ironic node-create -d your_driver agent_ipmitool \
                   -i ipmi_address=<ipmi_ip> \
                   -i ipmi_username=<ipmi_username> \
                   -i ipmi_password=<ipmi_password> \
                   -e compute_node=compute.node.id \
                   -u ironic_node_uuid

compute.node.id is the compute node ID saved in CCDM
(Compute Cluster Data Model)


2) On watcher, build the Baremetal Cluster Data Model (BCDM) by
periodically requesting Ironic service.
The Baremetal Cluster Data Model structure is shown as followings

{
  "uuid": "4f37180e-c310-4327-a286-d5ab9ffc6497",
  "power_state": "power on",
  "maintenance": false,
  "maintenance_reason": null,
  "extra": {"compute_node_id": 1}
  }

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
Watcher consumes some Ironic notifications. We leave this for future work,
which is described in the following bp:
https://blueprints.launchpad.net/watcher/+spec/update-bare-metal-data-model-by-ironic-notifications

Other end user impact
---------------------
Watcher may report a stale representation of the Ironic resources and to
reduce this staleness, they can reduce the syncing interval in the
configuration.

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
  <li-canwei2>
Other contributors:
  <alexchadin>,<yumeng-bao>

Work Items
----------
* Add baremetal data model.

Dependencies
============
None

Testing
=======
Unit test on the `Watcher Decision Engine`.
Tempest.

Documentation Impact
====================
System Architecture doc will be updated, since model drivers accesses
only nova and glance as of now.

References
==========
None

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Pike
     - Introduced
