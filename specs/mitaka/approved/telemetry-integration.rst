..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=======================================================================
Watcher Decision Engine should query metrics from the Ceilometer V2 API
=======================================================================

https://blueprints.launchpad.net/watcher/+spec/telemetry-integration

Watcher Decision Engine must query metrics from the Ceilometer V2 API to allow
an easiest integration with OpenStack services (especially devstack).

Telemetry used to be the initial name of the Ceilometer project. Now, the
following projects are managed by the Telemetry team:

-   **Aodh** - an alarming service
-   **Ceilometer** - a data collection service
-   **Gnocchi** - a time-series database and resource indexing service

Therefore, behind the word "*Telemetry*" we encompass the three projects.

Please, refer to `the official page of the Project <https://wiki.openstack.org/wiki/Telemetry>`_
if you want to know more about it.

Problem description
===================

Today, the watcher Decision Engine is not relying on Ceilometer V2 API to query
the metrics necessary for the optimization algorithm.

Use Cases
----------

This will address any use case where Watcher needs to be used for optimizing
an OpenStack cluster where Telemetry is being used for collecting metrics and
where the operators do not want to install any other metering chain.

It will impact every developer that has already developed an optimization
strategy in the Watcher project.

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

Estimated changes are going to be in the following places:

*   Modify the query of metrics on the available strategies (for example,
    **basic_consolidation**) to query Ceilometer API V2
*   May need to develop a helper to simplify some complex queries to the
    Ceilometer V2 API
*   Be compliant with the naming of Telemetry measurements

Alternatives
------------

No alternative because Watcher definitely needs to rely on Ceilometer API V2
to make sure it is compatible with any deployed OpenStack cluster.

Data model impact
-----------------

There is no impact on the Watcher MariaDB database (which stores Watcher
objects such as Audit Templates, Audits, Action Plans, ...).

But there is an impact on how Watcher will request the metrics in the Decision
Engine, especially regarding the measurements names because Watcher used to
have its own measurements naming system.

See `the full list of available measurements for Telemetry <http://docs.openstack.org/admin-guide-cloud/telemetry-measurements.html>`_

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
production environment.
These issues may now be solved thanks to an abstraction layer which enables
anybody to change the underlying metrics storage backend easily.

The metrics will now be queried by an optimization strategy using the python
Ceilometer client package corresponding to the Ceilometer V2 API.
This Ceilometer API will relay the query to an abstract Ceilometer Storage
Engine Base Interface (see class defined in **ceilometer.storage.base.py**).

The Storage Engine may be configured with any available driver for requesting
a time-series database implementation (InfluxDB, OpenTSDB, ...), providing much
better performances than a SQL database.
For example, see class **ceilosca.ceilometer.storage.impl_monasca.py** in the
**monasca-ceilometer** project.

The frequency of the queries will depend on the strategy used to achieve the
goal of the audit.

The performances of the query will not only depend on the underlying database
implementation but also on how it has been deployed and configured for indexing
the metrics:

-   sharding policy of the TSDB + use of a cluster of nodes to balance the load
-   tags associated to each metric (host id, instance if, ...),
-   use of pre-defined requests (named "Continuous Queries" in InfluxDB)

Other deployer impact
---------------------

Telemetry services will have to be installed on the controller nodes and
compute nodes of the OpenStack cluster that the admin wants to optimize with
Watcher.

The main configuration file **watcher.conf** will also be impacted, especially
the **watcher_metrics_collector** section.

The V2 of the Ceilometer querying API has been released since the official
Kilo release.
Therefore, this blueprint should deliver a Watcher version which would be
compatible with any deployment using the Kilo release and above.


Developer impact
----------------

There may be some change requests to the Telemetry team when some metrics are
not available and strongly needed for optimization strategies (Energy, ...).


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  jed56

Work Items
----------

Work items or tasks -- break the feature up into the things that need to be
done to implement it. Those parts might end up being done by different people,
but we're mostly trying to understand the timeline for implementation.


Dependencies
============

* https://wiki.openstack.org/wiki/Ceilometer/blueprints/APIv2

* https://blueprints.launchpad.net/ceilometer/+spec/api-v2-improvement

* https://wiki.openstack.org/wiki/Gnocchi

* http://docs.openstack.org/admin-guide-cloud/telemetry-measurements.html

Testing
=======

* Unit tests on the Watcher Decision Engine

* An admin should be able to launch an Audit with Watcher with a
  SERVERS_CONSOLIDATION goal on an OpenStack cluster which does
  not have the Watcher metering chain installed but only the
  Telemetry services.


Documentation Impact
====================

The documentation explaining howto add new optimization strategies will have
to indicate that metrics must be queried using the Ceilometer V2 client API.

References
==========

* Telemetry official project page: https://wiki.openstack.org/wiki/Telemetry

* http://eavesdrop.openstack.org/irclogs/%23openstack-meeting-3/%23openstack-meeting-3.2015-11-04.log.html

* See Gnocchi Features in https://wiki.openstack.org/wiki/ReleaseNotes/Liberty#OpenStack_Telemetry_.28Ceilometer.29

* https://wiki.openstack.org/wiki/Gnocchi

* Video presenting Ceilosca=Monasca+Ceilometer : https://www.youtube.com/watch?v=5-IvVwIoCzM

* Source code project of Monasca+Ceilometer : https://github.com/openstack/monasca-ceilometer

History
=======

None
