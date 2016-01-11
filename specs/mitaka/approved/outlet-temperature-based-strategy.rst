..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Outlet Temperature Based Strategy
==========================================

https://blueprints.launchpad.net/watcher/+spec/outlet-temperature-based-strategy

Outlet(Exhaust Air) temperature is a new thermal telemetry which can be used
to measure the server's thermal/workload status.

This spec proposes a new Watcher migration strategy based on the outlet
temperature of servers. This strategy makes decisions to migrate workloads
to the servers with good thermal condition (lowest outlet temperature) when
the outlet temperature of source servers reach a configurable threshold.

Note: "server" in this document means "hypervisor".

Problem description
===================

In current Data Center infrastructure, the cooling air supply to servers can
be different. When a server is overloaded or the supply air is too hot, the
outlet temperature telemetry can be used to detect the problem. In order to
have the server in a reliable thermal condition, some of the server's
workloads should be migrated to other server with safer thermal conditions.

Use Cases
----------

As an administrator, I want to be able to trigger an audit that controls the
temperature and perform workload load balancing.

In order to :

* Reduce the total power consumption spent on cooling.

* Increase the lifespan of the data center because cooling effectiveness is a
  first order factor.

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

Watcher already has its decision framework, so this strategy should be a new
class which extend the base strategy class.

* Set the threshold in 2 steps : hard coded first, then through the template.

* Create a new Python class to extend the "BaseStrategy" class.

* Use the Ceilometer client to get Outlet temperature metrics of hypervisors.

* Use the Nova objects framework to get free CPU/Memory/Disk of hypervisors.

* An algorithm to detect if the threshold of Outlet temperature has been
  reached and to choose the migration target server. It will filter the viable
  targets according to the free resource information of hypervisors from
  previous step.


Alternatives
------------

No alternative

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

There used to be some performance issues regarding the query of metrics from
the Ceilometer database. This is one of the reason why it was rarely used in
production environment. These issues may now be solved thanks to an
abstraction layer which enables anybody to change the underlying metrics
storage backend easily.
There is also a performance issue when you query the Nova DB to get cpu
usage metrics.

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
  <junjie-huang>


Work Items
----------

1. function to use Ceilometer client to get outlet temperature of hypervisors.

2. function to filter servers by Nova basic metrics(free CPU/Memory/Disk)

3. Rewrite execute function to add the algorithm to detect if the threshold
   of outlet T has been reached and choose the target hypervisor, generate
   action plan.


Dependencies
============

* https://wiki.openstack.org/wiki/Ceilometer/blueprints/APIv2

* https://blueprints.launchpad.net/ceilometer/+spec/api-v2-improvement

* http://docs.openstack.org/admin-guide-cloud/telemetry-measurements.html

* http://docs.openstack.org/developer/python-novaclient/api.html


Testing
=======

Unit tests and functional test, will use a fake metrics set for running
functional test.


Documentation Impact
====================

A documentation explaining how to use this new optimization strategy.


References
==========

http://www.intel.com/content/www/us/en/servers/ipmi/ipmi-home.html


History
=======

None
