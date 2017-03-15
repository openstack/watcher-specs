..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================
Support gnocchi in watcher
==========================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/gnocchi-watcher

Problem description
===================

Today, Watcher uses Telemetry and Monasca to collect metrics from the cluster.
We need to support gnocchi as well since ceilometer v2 API is deprecated.

Use Cases
---------

As administrator, I want to run strategies with Gnocchi support as data source
for metrics.

Proposed change
===============

We need to add support to data source gnocchi and implement
statistic_aggregation method, which will query from gnocchi service
for sample data.

Provide granularity[1] as input parameter to strategies.

Alternatives
------------

Monasca

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

Gnocchi should boost the overall performances of Watcher as compared to
Ceilometer.

Other deployer impact
---------------------

Gnocchi should be configure as backend for ceilometer.

Developer impact
----------------

Strategies developers need to adapt them to use Gnocchi.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <sanfern> santhosh.fernandes@gmail.com
  <alexchadin> a.chadin@servionica.ru

Work Items
----------

* Implement data source for gnocchi.
* Update all strategies to use gnocchi datasource as well.
* Add gnocchi_client section to watcher.conf file.
* Add api_version field under gnocchi_client section.
* Enable gnocchi plugin in local.conf.controller for devstack.

Dependencies
============

python-gnocchiclient needs to be installed.

Testing
=======

1. Unit tests and tempest tests should be updated.
2. Update multi node gate job

Documentation Impact
====================

Need to update the gnocchi support in configuration

References
==========

[1]https://docs.openstack.org/developer/gnocchi/glossary.html

History
=======

None
