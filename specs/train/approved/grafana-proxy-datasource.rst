..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================
Grafana proxy datasource
========================

https://blueprints.launchpad.net/watcher/+spec/grafana-proxy-datasaource

Watcher requires metrics from compute nodes and instances to perform the
resource optimization. Metrics are retrieved using several different
datasources such as Gnocchi and Monasca, however, not every OpenStack cloud
might have the available datasources deployed. Grafana can be implemented as an
additional datasource that can be used to retrieve metrics from
`several different databases`_ that the Grafana endpoint is configured to use.

.. _several different databases: https://grafana.com/plugins?type=datasource`

Problem description
===================

Not every OpenStack cloud might use the currently available datasources
limiting the use of Watcher. By offering a widely used monitoring platform as
datasource with flexible configurations options more OpenStack clouds could
start using Watcher.

Use Cases
----------

As a service operator I want Watcher to integrate with currently deployed
monitoring solutions.

As a service operator I want to limit the amount of external credentials I have
to configure for Watcher.

Proposed change
===============

The new Grafana datasource will be able to query for different metrics
depending on what is configured by the end user. Flexible configuration options
will allow Grafana to work for each user's configuration. Some of these options
will be configurable per metric using key value pairs in a dictionary. These
options are called maps as they map the value to a specific metric.
Configuration options include:

* Endpoint url
* Authorization token
* Project id map
* Attribute map
* Database map
* Translator map
* Query map

A configuration example configured for the ``host_cpu_usage`` and
``instance_cpu_usage`` metrics could look as follows:

::

  [grafana_client]
  token = uyyNKUJOZiLW7AVKRF7XAAAAQQDzoXbnS6cOxxcqJfS8ZEQyxgakF0bSUo0D==
  base_url = https://grafana.ch/api/datasources/proxy/
  project_id_map = host_cpu_usage:1337,instance_cpu_usage:4337
  metric_db_map = host_cpu_usage:production_db,instance_cpu_usage:production_db
  attribute_map = host_cpu_usage:hostname,instance_cpu_usage:human_id
  translator_map = host_cpu_usage:influxdb,instance_cpu_usage:influxdb
  query_map = host_cpu_usage:SELECT 100-{0}("{0}_value") FROM {3}.cpu_percent
              WHERE ("host" =~ /^{1}$/ AND "type_instance" =~/^idle$/ AND
              time > now()-{2}m),instance_cpu_usage:SELECT 100-{0}("{0}_value")
              FROM {3}.cpu_percent WHERE ("host" =~ /^{1}$/ AND "type_instance"
              =~/^idle$/ AND time > now()-{2}m)

Grafana uses project ids to proxy to different ``databases`` each of these
projects could contain a different type of ``database``. **The term project**
**will be used throughout this document to prevent possible confusion**.
All the desired metrics can be collected from multiple project or a single one
depending on how the monitoring is configured but is limited to a single metric
per project. This is because there is no method to aggregate a single metric
across multiple projects.

The way queries have to be sent to the endpoint and how to interpret the
retrieved data will depend upon the project behind Grafana. To account for
these differences between projects specific translators will be developed.
The influxdb translator will be developed first. The translator map is used
to perform the correct translations per metric depending on the type of
project.

Projects could contain one or more databases similar to schema's in MySQL. The
database map allows to define a specific database per metric.

Similar to the project map and the database map is the query map. This map
contains the queries that will be send to the project to retrieve metrics.
Queries are depended on the type of project and in the case of influxdb they
are similar to SQL statements.

The attribute map is used to select specific attribute from the resource
objects. This is necessary because the attribute used as identifier in projects
can differ per deployment and per metric.

From the query map the entries will be formatted so that essential information
for retrieving the specific metric for the desired host can be achieved.

::

  query = 'SELECT "{0}_value" FROM cpu_util WHERE host =~ /^{1}$/ AND time > '
          'now() - {2}m'
  query.format(aggregate, attribute, period, translator_specific)

The format options can be extended overtime in case other specific
projects such as elastic search require different parameters to successfully
build a query.

The initial format options will be:

* {0} = aggregate
* {1} = attribute
* {2} = period
* {3} = { influxdb: retention_period, }

Because the amount of metrics available to Grafana depends on user
configuration some minor changes are made to the datasource manager to build
the metric list for Grafana at runtime.

Instead of configuration many parameters using the default configuration file
`the metric yaml`_ can used to set the configuration but the expected
parameters differ from other datasources because of the large amount of
parameters.

::

  grafana:
    host_cpu_usage:
      project: 1337
      db: production_db
      attribute: hostname
      translator: influxdb
      query: SELECT 100-{0}("{0}_value") FROM {3}.cpu_percent
              WHERE ("host" =~ /^{1}$/ AND "type_instance" =~/^idle$/ AND
              time > now()-{2}m)

.. _the metric yaml: https://specs.openstack.org/openstack/watcher-specs/specs/train/approved/file-based-metricmap.html

Alternatives
------------

Datasources for individual projects that Grafana integrates with could be
developed but this would be significantly more development effort and possibly
complicate authorization as it would have to be configured per database.

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

The configuration file will need to contain the Grafana authorization token
which provides read access to the databases Grafana is configured for.
The configuration file already contains other important credentials.

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
  Dantali0n

Work Items
----------

* Configuration options
* General Grafana datasource
* Translator interface
* InfluxDB translator
* Unit tests for Grafana
* Unit tests for translators


Dependencies
============

* The communication with Grafana is realized using the requests library

Testing
=======

Unit tests for both the datasource itself as well as the translator base class
and any subsequent translators will be created.


Documentation Impact
====================

A page containing documentation on how end user's can configure the options
to successfully use Grafana as a datasource will be created.


References
==========

* https://specs.openstack.org/openstack/watcher-specs/specs/train/approved/formal-datasource-interface.html
* https://specs.openstack.org/openstack/watcher-specs/specs/train/approved/file-based-metricmap.html

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced

