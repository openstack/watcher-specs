..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Uniform Airflow Migration Strategy
==========================================

https://blueprints.launchpad.net/watcher/+spec/uniform-airflow-migration-strategy

Airflow (Unit: CFM) is a cooling related telemetry which can be used to measure
the cooling status of server.

This spec proposes a new Watcher migration strategy based on the airflow of
servers. This strategy makes decisions to migrate VMs to make the airflow
uniform.

Note: "server" in this document means "hypervisor".

Problem description
===================

In current Data Center infrastructure, the cooling air supply to servers can
be different , depends on the workload and inlet temperature. When a server is
overloaded or the supply air is too hot, the airflow can reach the threshold.
In this case, we need to move the VM instance to other servers.

Use Cases
----------

As an administrator, I want to be able to trigger an audit that controls the
airflow and perform VM instance load balancing.

In order to:

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

* Set the threshold through the template.
  see: https://blueprints.launchpad.net/watcher/+spec/optimization-threshold

* Create a new Python class to extend the "BaseStrategy" class.

* Use the Telemetry client to get Airflow, Inlet temperature, System Power
  metrics of hypervisors.

* Use the Nova objects framework to get free CPU/Memory/Disk of hypervisors.

* An algorithm to detect if the threshold of Airflow has been reached, by
  default it uses the average value in 5 minutes to compare with the threshold
  ,and can be configurable like threshold.
  Here it needs 3 thresholds: Airflow, Inlet temperature, and System power.
  When the threshold of Airflow has been reached, it will check:

    * Whether the threshold of both Inlet temperature and System power been
      reached, if so, it will choose the first VM to migrate.

    * Whether the inlet temperature and system power both lower than threshold
      if so, it means there might be someting wrong with the hardware, it will
      migrate all VMs of the hypervisor.

  At the end, it will filter the viable targets according to the free resource
  information of hypervisors from previous step.


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
the Telemetry database. This is one of the reasons why it was rarely used in
production environment. These issues may now be solved thanks to an
abstraction layer which enables anybody to change the underlying metrics
storage backend easily.
There is also a performance issue when you query the Nova DB to get CPU
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

1. function to use Telemetry client to get Airflow,Inlet temperature,System
   power of hypervisors.

2. function to filter servers by Nova basic metrics(free CPU/Memory/Disk).

3. Rewrite execute function to add the algorithm to detect the threshold and
   to choose the target hypervisors, generate action plans.


Dependencies
============

* https://wiki.openstack.org/wiki/Ceilometer/blueprints/APIv2

* https://blueprints.launchpad.net/ceilometer/+spec/api-v2-improvement

* https://blueprints.launchpad.net/watcher/+spec/optimization-threshold

* https://docs.openstack.org/admin-guide/telemetry-measurements.html

* https://docs.openstack.org/developer/python-novaclient/api.html


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