..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================
Energy Saving Strategy
======================

https://blueprints.launchpad.net/watcher/+spec/strategy-to-trigger-power-on-and-power-off-actions

This spec describes a new strategy to trigger "power on" and "power off"
actions in watcher, which can save energy for those data centers who use
watcher to do the resource optimization.

Problem description
===================

For a data center with large amount of VMs and physical hosts,the total power
consumption is tremendous. When workload is not heavy, Watcher can be used to
reduce power consumption by triggering a request to power off some idle hosts
without VMs. And when the workload increases Watcher will trigger a "power on"
request to fulfill the service requirements.

This "energy saving" goal can be fulfilled by adding the following subfeatures
in Watcher:
#. Add new actions "power on" and "power off" in Watcher.
#. Implement a new strategy to generate 'power on' and 'power off' actions.

This spec implements the second feature: Implement a new strategy to generate
"power on" and "power off" actions.

Use Cases
----------

As an openstack operator, I want to keep my data center energy-efficient.
When the workload is low, shut down some idle hosts to save energy, and when
the workload goes high, power them on to ensure the QoS.

As a developer,I need a strategy to trigger the "power on" and "power off"
actions in watcher.

Proposed change
===============

* Add one new goal - "energy saving"

* Add one new strategy - "Energy Saving Strategy"

* The detailed policy in "energy saving strategy" can be described as
  the followings:

  In this policy, a number (min_standby_nodes_num) of standby nodes is
  given or calculated. The standby nodes refer to those nodes unused
  but still powered on to deal with boom of new instances.

  If the number of unused nodes(in poweron state) is larger than the given
  number, randomly select the redundant nodes and power off them;
  If the number of unused nodes(in poweron state) is smaller than the
  given number and there are spare unused nodes(in poweroff state), randomly
  select some nodes(unused,poweroff) and power on them.

  In this policy, in order to calculate the given number
  (min_standby_nodes_num), users must provide two parameters:

  * One parameter("standby_nodes_int") is a number of standby nodes.
    This number should be int type and larger than zero.

  * Another parameter("standby_used_percent") is a percentage number, which
    describes the quotient of number_of_standby_nodes/number_of_nodes_with_VMs,
    where number_of_nodes_with_VMs is the number of nodes with VMs running on
    it. Given this percentage and number_of_nodes_with_VMs, we can easily get
    number_of_standby_nodes. The nodes with VMs refer to those nodes with VMs
    running on it.

  Then chose the larger one as min_standby_nodes_num:
  min_standby_nodes_num = max(standby_nodes_int, number_of_standby_nodes)


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

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <li-canwei2>,<yumeng-bao>

Work Items
----------
* Add one new goal - "energy saving"

* Add one new strategy - "Energy Saving Strategy"

* Complete the main functions policy in "energy saving strategy"

  #. Complete get_hosts_pool function to Classify all the nodes
     into three types and count their numbers: nodes_with_vms,
     unused_poweron, unused__poweroff.

  #. calculate the "min_standby_nodes_num" with two given parameters:
     "standby_used_percent" and "standby_used_int"

  #. Write the execute function to compare the number of "unused_poweron
     nodes" with "min_standby_nodes_num" and decide which nodes should be
     power on/off.

Dependencies
============

https://blueprints.launchpad.net/watcher/+spec/add-power-on-off

Testing
=======

Unit and functional test are needed.

Documentation Impact
====================

Add docs on how to use this strategy.

References
==========

None

History
=======

None

