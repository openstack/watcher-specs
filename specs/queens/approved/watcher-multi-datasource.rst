..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================
Support multi datasource in watcher
===================================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/watcher-multi-datasource

Problem description
===================

Today, Watcher supports Telemetry, Monasca and gnocchi to collect metrics from
the cluster. There is a helper class for each respective datasource type
implements query and provides the results. We need to create datasource
abstract class which will define methods for all the metrics capability
methods. These methods have to be implemented by respective datasource helper
class.

Use Cases
---------

As administrator, I want to run strategies to specific datasource backend.

Proposed change
===============

1. Define a common abstraction layer for all datasources. Define get methods
   for all metrics used by current strategies. It also contains metric map
   which maps strategy metric requirements to datasource metric name.

   .. code-block:: python

      class DatasourceBase(object):

          METRIC_MAP=dict(datasource=dict(metric_name_watcher=
                                          metric_name_datasource,),)

          @abc.abstractmethod
          def get_host_cpu_usage(self, resource_id, period, aggregate,
                                 granularity=None):
              raise NotImplementedError

          @abc.abstractmethod
          def get_instance_cpu_usage(self, resource_id, period, aggregate,
                                     granularity=None):
              raise NotImplementedError

2. Update all the existing datsource helper classes as the child class of
   DatasourceBase class. Implement abstract methods of DatasourceBase class in
   ceilometer, monasca and gnocchi classes.

3. Support metric data collection from multiple datasource. User can define
   datasource priority in watcher.conf, we can use the existing configuration
   by changing it type to list.::

      [watcher_strategies.basic]
      datasource = ceilometer, gnocchi, monasca

   This can be done in two ways

    i.  calculate the datasource_backend value on strategy basis. check, if
        meters used by the strategy available in first priority datasource,
        choose that backend for all subsequent requests for that audit request.

    ii. calculate the datasource_backend on metric basic, ie each the strategy
        request to get some metric data, calculate the value of
        datasource_backend on the basis or priority set in conf file and
        availablity of the metric in choosen datasource.

    option second has overhead of choosing datasource each time the request
    arrives, but has advantage that if a metric is not available in one
    datasource it can check for other. with current watcher strategy
    requirements option first will suffice.

4.  Define a datasource manager class to calculate the datasource
    backend.

    .. code-block:: python

       class DatasourceManager(object):

           def get_backend(self, metrics):
           ''' returns: object of DatasourceBase child
               class '''

5. Update existing strategies to use new datasource classes, Make the
   datasource_backend property abstract in strategy base class.

   .. code-block:: python

      class BasicConsolidation(base.ServerConsolidationBaseStrategy):

          @property
          def datasource_backend(self):
              self.datasource_backend = manager.DataSourceManager(
                  config=self.config,
                  osc=self.osc
                  ).get_backend(self.METRIC_NAMES)
              return self._datasource_backend

         def get_node_cpu_usage(self, node):
             resource_id = "%s_%s" % (node.uuid, node.hostname)
             return self.datasource_backend.get_host_cpu_usage(
                 resource_id = resource_id,
                 period=self.period,
                 aggregate = 'avg',
                 granularity=None
                 )

Alternatives
------------
If we keep the existing implementation, each strategy has to use the
specific interfaces of the data source driver provides. It makes the
implementation of strategies highly coupled with a specific data source.


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

Using Multiple Datasource can degrade the overall openstack cluster
performance.

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
    adi-sky17

Work Items
----------

* Implement base class for all datasource drivers.
* Define abstract get methods for all meters used by existing strategies.
* Implement abstract methods in ceilometer, monasca and gnocchi classes.
* Update existing strategies to use the new format.

Dependencies
============

None

Testing
=======

Unit tests need to be updated

Documentation Impact
====================

Plugin documents should be updated.
https://docs.openstack.org/watcher/latest/contributor/plugin/strategy-plugin.html#querying-metrics

References
==========

None

History
=======

None
