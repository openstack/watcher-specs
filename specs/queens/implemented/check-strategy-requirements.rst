..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===============================
Check the strategy requirements
===============================

https://blueprints.launchpad.net/watcher/+spec/check-strategy-requirements

Problem description
===================

Running of `strategy`_ requires different type of data resources to compute
a `solution`_. First launch of specified strategy causes an error in most
cases. Admin has to take a look at logs to get more information about error.
It takes a lot of time and is not informative way.

Use Cases
---------

As an OpenStack `administrator`_, I want to be able to check strategy
requirements before strategy's launching.

As an OpenStack administrator, I want to be able to see list of strategy's
requirements along with thier states. This list should get me a conclusion if I
can execute selected strategy.

Proposed change
===============

There are some requirements which are to be accomplished:

* Metering service should be reachable. (mandatory)
* One or more metrics associated with strategy should be presented in metering
  service. (optional)
* Cluster Data Model used by the strategy should be loaded. (mandatory)

Checking of strategy can be called by using command 'watcher strategy state
{name_of_strategy}'. It will show the following table:

+--------------------+-----------+------------------------------+-----------+
| Requirement type   | Mandatory | State                        |  Comment  |
+====================+===========+==============================+===========+
| Metering Service   |    yes    | Gnocchi: available           |           |
+--------------------+-----------+------------------------------+-----------+
| Metrics            |    no     | | cpu_util: available        | |comment| |
|                    |           | | memory.used: not available |           |
+--------------------+-----------+------------------------------+-----------+
| Cluster Data Model |    yes    | Compute: available           |           |
+--------------------+-----------+------------------------------+-----------+

.. |comment| replace:: cpu_util is out of bounds (144.2 > 100)

Metering service can be verified by calling one of API resources (response
should return HTTP status code 200):

* GET /v1/status for Gnocchi
* GET /v2/resources for Ceilometer API
* GET /v2.0/metrics for Monasca API

API versions are set via conf/{metering_serice}_client.py

Metering service for each strategy is defined in watcher.conf file.
If chosen metering service isn't available, state of metering service should be
tagged as 'not available'. Otherwise, state would be 'available'.

Watcher should know which metrics are used by requested strategy. This can be
reached by using METRIC_NAMES dictionary. This dict contains datasources as
keys and their subdicts of strategy_metric_name:datasource_metric_name pairs.
This form of used strategy metrics is already used by `basic_consolidation`_,
`outlet_temp_control`_, `uniform airflow`_, `vm_workload_consolidation`_
strategies. Other strategies should be adapted to use METRIC_NAMES. I would
also propose to set min and max bounds for metrics to be sure that requested
metric will come in the form of expected unit (i.e. 0.00-100.00 for cpu_util).

Availability of metrics can be verified by sending appropriate requests to
the metering service. For example, gnocchi will return list of metrics in
response to GET /v1/metric request. It isn't required to have all strategy
metrics in metering service cause some strategies allows to work with some
metrics, not all.

`Cluster Data Model`_ will be loaded in _collectors struct of CollectorManager
class if appropriate collector is defined in collector_plugins option. By
default, there is only compute CDM.

Alternatives
------------

None.

Data model impact
-----------------

None.

REST API impact
---------------

GET /v1/strategies/(strategy)/state

Parameters:

* strategy (unicode) - UUID or name of the strategy.

Return: List of strategy's requirements and their states.

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

None.

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
  alexchadin <a.chadin@servionica.ru>

Work Items
----------

There are the following steps to be done:

* Add new command to strategy API that will check out requirements.
* Adapt existing strategies to use METRIC_NAMES dictionary.
* Update python-watcherclient to support new command.

Dependencies
============

None.

Testing
=======

New unit tests should be added along with updating old ones.

Documentation Impact
====================

Related documentation should be added.

References
==========

.. _administrator: https://docs.openstack.org/watcher/latest/glossary.html#administrator
.. _strategy: https://docs.openstack.org/watcher/latest/glossary.html#strategy
.. _solution: https://docs.openstack.org/watcher/latest/glossary.html#solution
.. _basic_consolidation: https://github.com/openstack/watcher/blob/1.4.1/doc/source/strategies/basic-server-consolidation.rst
.. _outlet_temp_control: https://github.com/openstack/watcher/blob/1.4.1/doc/source/strategies/outlet_temp_control.rst
.. _uniform airflow: https://github.com/openstack/watcher/blob/1.4.1/doc/source/strategies/uniform_airflow.rst
.. _vm_workload_consolidation: https://github.com/openstack/watcher/blob/1.4.1/doc/source/strategies/vm_workload_consolidation.rst
.. _Cluster Data Model: https://docs.openstack.org/watcher/latest/glossary.html#cluster-data-model-cdm

