..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Add Prometheus as a Watcher Data Source
==========================================

launchpad blueprint: https://blueprints.launchpad.net/watcher/+spec/example

Watcher currently supports a small number of data sources for collection of
metrics: Ceilometer, Gnocchi and Grafana. Prometheus is a widely adopted
time/series based metric collection system that allows for collection of any
type of custom metric an operator may be interested in for their cloud VMs or
containers.

Besides its usage in OpenStack deployment, Prometheus is considered Kubernetes
'native' as both are CNCF projects and Prometheus is included as part of
Kubernetes distributions.

Adding the ability for Watcher to interact with a Prometheus data source
will increase the potential user base for Watcher and especially to those
operators that are familiar with or already using Prometheus.

Problem description
===================

Watcher currently supports a small number of data sources for collection of
metrics: Ceilometer, Gnocchi and Grafana. Some of these are no longer actively
developed and integrated with OpenStack distributions, limiting the ability
to deploy watcher at all.

As Prometheus becomes the de facto standard metrics store in the Kubernetes
ecosystem and OpenStack is increasingly deployed on Kubernetes, Watchers'
inability to consume metrics from Prometheus limits the project's reach.

Use Cases
----------

By providing the ability to couple the efficient and highly customizable
Prometheus collector with the Watcher project operators can achieve a powerful
optimization solution for their OpenStack deployments. There is currently no
way to use Prometheus as a data source for Watcher.

As an operator with existing knowledge of Prometheus, I would like to
leverage the power of Watcher as an optimization engine, by using it as a data
source.

As an operator with existing Kubernetes infrastructure, I would like to reuse
the same metrics storage solution across my OpenStack and Kubernetes
deployments.

As a developer of Watcher, I want to allow it to be deployed in more OpenStack
clouds, leveraging popular open-source tools to increase the project's reach
and adoption.

Proposed change
===============

A new Prometheus module will be added to watcher.decision_engine.datasources
which will leverage the https://opendev.org/openstack/python-observabilityclient
already used by AODH to retrieve metrics from Prometheus.
https://github.com/openstack/aodh/commit/f932265290a4e923eac6111eb28578489c7dce33

As a first implementation, we are not expecting to extend the DataSource
METRIC_MAP beyond the existing set (host/instance cpu/ram etc). That could be
considered future work depending on the success of this proposal.
The new Prometheus client will provide a default set of mappings to enable a
subset of strategies and goals to function by normalising the Prometheus
metric names and units to align with the existing values supported by other
data sources.

This initial work will not utilise Prometheus alert to enable triggering
audits and instead will build on AODH's existing integration to fulfil that
use case.

Alternatives
------------

It is not possible to use Prometheus as a metrics collector currently. The
alternative is to use one of the currently supported data sources which
restricts the potential user base for Watcher.

Data model impact
-----------------

There are no expected changes to the data model as part of this proposal.
Given the extensibility of Prometheus as a collector, it is feasible that
future work could propose extension of the Watcher metrics beyond the
current set (host/instance cpu or ram usage, temperatore etc). However
that is not in the scope of this current proposal.

REST API impact
---------------

This proposal is not expected to impact the REST API.

Security impact
---------------

None Expected

Notifications impact
--------------------

None expected.

Other end user impact
---------------------

None expected.

Performance Impact
------------------

There is no expected impact to using a Prometheus data source compared
to any of the currently supported sources.

Other deployer impact
---------------------

No anticipated impact besides the ability to integrate with a new data source.
Deployers will have to provide the required configuration values such
as (Prometheus) authentication credentials required for the integration.

A new optional dependency on python-observabilityclient will be introduced
which may require changes to packaging and installers.

Developer impact
----------------

The watcher devstack plugin will be extended to allow developers to use
Prometheus instead of the default Gnocchi/Ceilometer collectors.

Implementation
==============

Assignee(s)
-----------

Sean Mooney, Marios Andreou,

Reviewers
-----------

Dan Smith

Work Items
----------

We will need:

  * New prometheus.py subclass of base.DataSourceBase in the [datasources](https://github.com/openstack/watcher/tree/master/watcher/decision_engine/datasources),
  * A prometheus_client.py to handle authentication and transport of metrics
    from the Prometheus instance under
    [conf](https://github.com/openstack/watcher/tree/master/watcher/conf),
  * Extend the Zuul CI testing for the Prometheus integration, that is, add a
    new devstack job similar to the existing
    [watcher-tempest-strategies](https://zuul.opendev.org/t/openstack/builds?job_name=watcher-tempest-strategies&project=openstack/watcher)
    to enable Watcher with a Prometheus collector.
  * Extend the Watcher devstack plugin to support deployment with Prometheus
    instead of the default Gnocchi/Ceilometer.

Dependencies
============

The proposal requires that the OpenStack deployment monitored by the Prometheus
instance used as a data source, has deployed the appropriate exporters, the
actual collection functions and API endpoints, such that they can be mapped to
the expected Watcher metrics (host_cpu_usage, host_ram_usage,
instance_cpu_usage etc).

Testing
=======

As mentioned under work items this work will also include addition of a new
CI job against the Watcher code repo. Beyond ensuring the integration point
(e.g. communication with Prometheus is OK, metrics are received and processed
correctly etc) ideally this should include functional testing similar to the
existing watcher-tempest-strategies job that has execution of strategies.

Documentation Impact
====================

We will need to extend documentation including considerations around setup,
for example, setting up the appropriate exporters on the Prometheus side,
best practices around authentication/certs etc.

References
==========

This proposal was first mentioned by S Mooney during the
[October 2024 Watcher PTG session](https://etherpad.opendev.org/p/oct2024-ptg-watcher)
session

