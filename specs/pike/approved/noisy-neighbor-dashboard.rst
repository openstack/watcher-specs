..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================
Noisy neighbor dashboard
========================

https://blueprints.launchpad.net/watcher-dashboard/+spec/noisy-neighbor-dashboard

Following the implementation of the `noisy-neighbor-strategy blueprint`_,
Watcher now has all of the necessary prerequisites in order to provide L3
cache and memory metrics to the operator.  This blueprint will focus on
collecting this resource consumption data and displaying it in a series of
graphs for operator monitoring and consumption.


Problem description
===================

There is currently no way for an operator to easily access and visualize
L3 cache and memory bandwidth consumption data on a per VM basis recorded
by Watcher.

Use Cases
---------

As an OpenStack operator, I need to view the noisy neighbor for L3 cache
and memory bandwidth metrics to make sure my nodes have good isolation and
performance.

As an OpenStack operator, I want to view IPC vs cache occupancy data.

As an OpenStack operator, I want to view IPC vs memory bandwidth data.

As an OpenStack operator, I want to view the memory bandwidth delta vs VM ID.

As an OpenStack operator, I want to view CPU steal vs VM ID.


Proposed change
===============

A Grafana template will be designed to display the desired data and will
integrate with both Gnocchi and Monasca telemetry collection services.

Alternatives
------------

A new watcher-dashboard change is needed to display graphs of the above
use cases.

Data model impact
-----------------

None.

REST API impact
---------------

None.

Security impact
---------------

None.

Notifications impact
--------------------

None.

Other end user impact
---------------------

None.

Performance Impact
------------------

Possible minor performance drop when viewing data plotting.


Other deployer impact
---------------------

None.

Developer impact
----------------

None.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  christopher-m-spencer

Work Items
----------

* New Grafana spec will be designed for noisy neighbor strategy.
* Collect cache occupancy and memory bandwidth data and output to plots.


Dependencies
============

* `noisy-neighbor-strategy blueprint`_
* `telemetry-measurements`_
* `grafana templates`_

Testing
=======

These graphs will have to be tested mainly via integration tests and visual
inspection.


Documentation Impact
====================

None.


References
==========

None.

.. _noisy-neighbor-strategy blueprint: https://blueprints.launchpad.net/watcher/+spec/noisy-neighbor-strategy
.. _telemetry-measurements: http://docs.openstack.org/admin-guide-cloud/telemetry-measurements.html
.. _grafana templates: http://docs.grafana.org/reference/templating/