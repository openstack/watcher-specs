..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=================================================================
Support multitenancy with the Prometheus datasource through Aetos
=================================================================

launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/prometheus-multitenancy-support

The telemetry team is working on adding multi-tenancy capabilities and Keystone
based authentication for metrics stored in Prometheus by developing the Aetos
reverse-proxy. Support for Aetos needs to be added into watcher.

Problem description
===================

Currently Watcher supports Prometheus as a metric datasource, with optional
basic auth or mtls. But Prometheus doesn't support multi-tenancy or rolebased
access control so common througout the openstack services.
To address this, the telemetry team is working on a reverse-proxy called Aetos
to allow using keystone authentication and roles for multi tenancy similarly
to how it's currently being done with Gnocchi. Watcher currently doesn't
support communicating with Aetos and so Watcher needs to be enhanced to
support Aetos as a new datasource

Use Cases
---------

As a deployer, I would like to provide more security for stored metrics by
disabling outside access to Prometheus and implementing RBAC via the Aetos
Reverse proxy server.

Proposed change
===============

Description of Aetos from Watcher's point of view:

Aetos is a reverse-proxy, which is deployed in front of Prometheus. Aetos
exposes a subset of Prometheus's http API and requiring and validating keystone
token with each request. The token is inspected for the roles of the user
sending the request. It's expected from Watcher to attach a token with either
a admin or service role. If this happens correctly, then each request is
forwarded unchanged to Prometheus and Prometheus's response is forwarded
without changes back to Watcher. The complete PromQL language is supported
and all APIs required by Watcher are supported as well. It's expected for Aetos
to always have an endpoint registered in keystone with service type
'metric-storage'.

The needed changes to add the support are these:

A new Aetos datasource will be added.
The current PrometheusHelper class will be turned into a baseclass or a
mixin. This will be shared between the PrometheusDirect and Aetos
datasources.
The __init__ and _setup_prometheus_client methods will
be implemented in the Aetos datasource class and will use keystone endpoints
to get Aetos's endpoints instead of using the host and port values from the
configuration.
The new data souce will preserve the 1:1 mapping between datasources and
python classes while ensuing the query logic is implemented in the base class.

A new configuration section for Aetos, will be added which would have options
to confiugre keystone endpoint discoveray and the lables to used for host
and instance metrics.

For the PrometheusDirect datasource, we will use the current implementation,
which uses the host and port values from the configuration.

When inialising the PrometheusAPIClient the Aetos datasource,
will constuct a keystone session and provide it to the PrometheusAPIClient
object.

If the `aetos` service is not registered in Keystone, the Aetos datasource
will exit with an error, which prevents the decision engine from starting.
Configuring the Prometheus and Aetos datasources at the same time
will be considered a configuration error.

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

We expect an increase in security on the metric storage side, which is the
whole purpose of the change. Authentication will be required for metric access

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

There is a slight performance impact. Since Aetos acts as a reverse proxy
in front of Prometheus, there is an additional step for each request in
comparison with sending requests directly to Prometheus. So a slightly longer
delay for each request is expected.

Other deployer impact
---------------------

The configuration option 'watcher_datasources.datasources' will have a new
valid value: 'aetos'

There will be a new configuration section called 'Aetos' with the following
options:

interface

    Type:
        string
    Default:
        public
    Valid Values:
        internal, public, admin

    Type of endpoint to use in keystoneclient.

region_name

    Type:
        string
    Default:
        <None>

    Region in Identity service catalog to use for communication with the
    OpenStack service.


fqdn_label

    Type:
        string
    Default:
        fqdn

    The label that Prometheus uses to store the fqdn of exporters. Defaults
    to ‘fqdn’.

instance_uuid_label

    Type:
        string
    Default:
        resource

    The label that Prometheus uses to store the uuid of OpenStack instances.
    Defaults to ‘resource’.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

jwysogla

Work Items
----------

* Use newer python-observabilityclient
* Convert the current PrometheusHelper class into a base class or a mixin.
  The __init__ and _setup_prometheus_client methods are to be implemented
  in classes that inherit from it.
* Create a class for implementing the Prometheus datasource, which
  inherits from the base class and uses the current implementation
  of the __init__ and _setup_prometheus_client methods.
* Add a configuration section for Aetos datasource, with the following options
  "interface", "region_name", "fqdn_label", "instance_uuid_label".
  Descriptions and values should be the same as in existing clients config
  sections.
* Add Aetos as a possible datasource
* Create a class for implementing the Aetos datasource, which inherics from
  the Prometheus base class/mixin, but implements different __init and
  _setup_prometheus_client methods.
* The Aetos datasource class uses keystone endpoints to get Aetos's endpoints.
* The Aetos datasource class creates a PrometheusAPIClient similarly to how
  it's already being created for prometheus, but
  also specifies a keystone session and a root_path, which is extracted from
  Aetos's endpoint.
* Add a tempest job similar to watcher-prometheus-integration, which will
  be configured to use the new Aetos datasource instead of Prometheus directly

Dependencies
============

python-observabilityclient 1.0.0 or newer

Testing
=======

* The current watcher-prometheus-integration job can be duplicated and
  modified slightly to be deployed with Aetos, using Aetos's devstack plugin.

* Unit tests would be added as well

Documentation Impact
====================

Add a new Aetos datasource section in the documentation. The contents should
be fairly similar to the current Prometheus documentation. The differences
would be mostly in the configuration options used. In comparison to
Prometheus, there is no need for "host", "port" or any authentication
or TLS options. But instead we will need to know the "interface" and
"region_name" as with most of other clients.

A mention will be added, that having a Prometheus and Aetos datasources at
the same time isn't supported and ends with a configuration error.


References
==========

* A bug with a related discussion: https://bugs.launchpad.net/watcher/+bug/2108855
* The whole effort for adding tenancy and authentication support for
  Prometheus was discussed during the telemetry PTG
  https://etherpad.opendev.org/p/apr2025-ptg-telemetry

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2025.2
     - Introduced
