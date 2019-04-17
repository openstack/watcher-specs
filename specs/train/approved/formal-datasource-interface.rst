..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===========================
Formal Datasource Interface
===========================

https://blueprints.launchpad.net/watcher/+spec/formal-datasource-interface

Different strategies pass different values to parameters of datasource methods
while these should be unified as implied by the datasource base class. The
formalizing of the datasource base class will ensure that all strategies can
work regardless of the underlying datasource. Additionally, the return types of
methods should also be unified.


Problem description
===================

Watcher strategies rely on specific datasources to work while strategies should
work regardless of the underlying datasource. The incompatibilities are due to
different types of values being passed to the parameters of methods. Most of
these problems are artifacts of back when there was no datasource base class.

Use Cases
----------

As end users I want strategies to work regardless of the datasource I have
deployed.

As developer I want to more easily develop or improve new strategies while
minimizing how much I should worry about the underlying datasource.


Proposed change
===============

The datasource base class is changed and comments are added to describe
expected values and units for parameters. For some parameters were the value
can be one of a set of options the list of options is maintained in a list in
the base class.

The new lists will be ``AGGREGATES`` and ``RESOURCE_TYPES``. ``AGGREGATES``
contains all the possible options to pass to the aggregate parameter.

The possible options for ``AGGREGATES`` are ``mean``, ``min`` and ``max``.
Mean will replace every instance of ``avg`` and is preferred as it is less
ambiguous.

::

  AGGREGATES = ['mean', 'min', 'max', 'count']

Many different parameters are shared across different methods and they share
the same types of values. These parameters are

* resource_id
* period
* granularity
* aggregate

The ``resource_id`` is renamed to ``resource`` and should be the object
retrieved for the specific resource but more context about the resource should
be passed to the datasource. The ``RESOURCE_TYPES`` list addresses this needed
context. It contains all possible types of resources this will allow the
datasource to access the object attribute it needs for data retrieval.

.. code-block:: python

  RESOURCE_TYPES = ['compute_node', 'instance', 'bare_metal', 'storage']

The resource types is required to access the correct attributes of the resource
object as the names of attributes vary between objects.

.. code-block:: python

  """Demonstration accessing the same data from different objects"""
  if resource_type == 'compute_node':
    hostname = resource.hypervisor_hostname
  elif resource_type == 'instance':
    hostname = resource.name

  raw_kwargs = dict(
    name=meter_name,
    start_time=start_timestamp,
    end_time=end_timestamp,
    dimensions={'hostname': hostname},
  )

The names of the resource are based on names in the helper classes to simplify
accessing these APIs. The method names in the ``ironic_helper`` are will be
changed to better fit the names in other helpers such as ``cinder_helper``.

The ``period`` is be used to specify the amount of time in seconds that is
used to aggregate metrics.

The ``granularity`` is be used to specify the interval between the time
series in seconds.

The ``aggregate`` parameter is already covered as the values are chosen from
``AGGREGATES``.

The ``statistic_aggregation`` method no longer uses the ``meter_name`` values
from the ``METRIC_MAP`` dictionary as identifier but will use the keys instead.
The datasources can still use the values of the ``METRIC_MAP`` to determine how
to retrieve metrics from their databases. The parameter ``aggregation`` is
renamed to ``aggregate`` to match the names used by other methods. The
parameters ``group_by`` and ``dimensions`` are removed.

The definitions off most methods in ``DataSourceBase`` will now look as detailed
below.

.. code-block:: python

  def statistic_aggregation(self, resource=None, resource_type, meter_name=None,
                            period=300, granularity=300, aggregate='mean')

  def get_host_cpu_usage(self, resource, resource_type, period, aggregate,
                         granularity=None)

  def get_host_memory_usage(self, resource, resource_type, period, aggregate,
                            granularity=None)


The expected values and return types will be documented in the DataSourceBase
using code blocks.

.. code-block:: python

  @abc.abstractmethod
  def get_host_cpu_usage(self, resource, resource_type, period, aggregate,
                        granularity=None):
      """ Get the amount of cpu usage for the host

      :param resource: The object returned by clients such as Server or
      Hypersivor when calling nova.servers.get or nova.hypervisors.get
      :param resource_type: The Type of the resource object selected from
      RESOURCE_TYPES.
      :param period: The amount of seconds back in time metrics are aggregated
      over.
      :param aggregate: The method to aggregate data selected from AGGREGATES.
      :param granularity: Interval between collected data in seconds.
      :return: Percentage of total cpu usage represented by float between 0-100
      """

Not all datasources will be able to implement all these different options.
As example some datasource do not support granularity and most do not support
the ``count`` aggregate. These incompatibilities should be met with reasonable
alternatives and warnings but throwing errors should be avoided.

Finally, the ``list_metrics`` and ``check_availability`` methods are used
by the API to return information on strategies when executing the ``state``
call.

Alternatives
------------

Accepting that certain strategies only work with specific datasources.

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

None

Other deployer impact
---------------------

None

Developer impact
----------------

All strategies and some datasource will have to be adapted to be compatible
with the new DataSourceBase and this will require development effort.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <Dantali0n>

Work Items
----------

* Change DataSourceBase according to new interface specification.

* Write comments in DataSourceBase to document interface.

* Adapt existing datasources to work with new interface.

* Change unit tests to work with new interface.


Dependencies
============

None


Testing
=======

Current datasource tests have to be adopted to work with the new datasource
base class. With the removal of the ``dimensions`` parameter the Monasca test
cases will require the most changes.

In addition to unit tests the correct functionality of the datasources are
examined in a working environment such as devstack.


Documentation Impact
====================

None


References
==========

None


History
=======

None
