..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================================
Add new actions "power on" and "power off" in Watcher
=====================================================

https://blueprints.launchpad.net/watcher/+spec/add-power-on-off

For a data center with large amount of VMs and physical hosts,the total power
consumption is tremendous. When workload is not heavy, Watcher can be used to
reduce power consumption by triggering a request to power off some idle hosts
without VMs. And when the workload increases watcher will trigger a "power on"
request to fulfill the service requirements.

This feature includes four sub-features:

* Build a new baremetal data model in Watcher.
* Add new actions "power on" and "power off" in Watcher.
* Implement a new strategy based on 'baremetal' and 'compute' data models,
  which could trigger 'compute' and 'baremetal' actions.
* Update bare metal data model by ironic notifications.

This spec implements the second sub-feature:Add new actions "power on" and
"power off" in Watcher.

Problem description
===================

The telecommunication network traffic tidal [1] is an actual phenomenon
in the telecommunication. For example, during the daytime, large amount
of users gather in the CBD[2] area and the workload of network traffic
system is high. When they get off work, the number of users declines
rapidly and so does the network traffic workload. The problem is how
to fulfill user network service requirements with minimal energy
consumption given the changing network traffic workloads.

As a real case from ZTE corporation, this problem is addressed by the
following way. Firstly, a boundary value is set to describe the maximum
percentage of idle hosts in a cluster, which is configurable by User.
When the ratio of idle hosts gets higher than the boundary value, we
power off some idle hosts until the ratio reduces to the boundary value.
Correspondingly, when this ratio becomes lower than the preset value,
we power on some hosts until the ration increases to the boundary value.

The feature in this spec will implement only the power on and power off
actions, the feature of deciding which hosts will be powered off/on according
to a boundary value will be left for future work.

Use Cases
---------

As a deployer, I want to have a "power off" action in watcher to help reduce
energy consumption by automatically cutting down the number of running hosts
when workload is low.

As a deployer, I want to have a "power off" action in watcher to automatically
increase the number of running hosts when workload increases and requires
more resources.

Proposed change
===============

Given the target hosts, we use Ironic Client to call IPMI tools to do the
"power on" and "power off" actions through the follwing Ironic API:
https://developer.openstack.org/api-ref/baremetal/?expanded=change-node-power-state-detail

Host state verification before executing the power on/off audit.

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
None

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

Test this new action using unit test. Or as an alternative, developer
can use an actuator strategy to allow excplicit action execution.
This actuator strategy is described in the following patchset:
https://review.openstack.org/#/c/425110/.

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
Acquire target hosts from Watcher baremetal data model.
Implement action:'change_node_power_state',where the input parameters
of this action is 'on' or 'off'.

Dependencies
============

This feature is in dependent with the following blueprint:
https://blueprints.launchpad.net/watcher/+spec/build-baremetal-data-model-in-watcher

Testing
=======

* Unit tests
* Tempest test

Documentation Impact
====================
None

References
==========
[1]http://ieeexplore.ieee.org/abstract/document/7179335/
[2]https://en.wikipedia.org/wiki/Central_business_district
[3]https://developer.openstack.org/api-ref/baremetal/?expanded=show-node-details-detail#Response

History
=======
None

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Pike
     - Introduced
