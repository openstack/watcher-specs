..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================
Time Series Framework
=====================

https://blueprints.launchpad.net/watcher/+spec/time-series-framework

Strategies are currently limited to obtain information about metrics in
an aggregated form for the most recent measurements. This limits what
strategies can achieve as they are unable to retrieve information about past
occurrences or information about periodic patterns. Currently, an audit will
have to be launched at the same time a specific situation is occurring in order
for the strategy to be able to identify this. A time series framework will
allow datasources to provide metrics over specific periods without aggregation,
allowing strategies to detect periodic patterns such as a weekly contention and
resolve these accordingly.


Problem description
===================

Strategies can only obtain metrics about the current state and not retrieve any
metrics over specific periods, in addition, strategies can only obtain an
aggregated value over the entire period instead of obtaining a time series.
Effectively, this limits the usability of strategies as they are unable to
detect any periodic patterns or resolves issues which occur sporadically.
Combined with that it generally takes a long time to run an audit this
complicates detecting problems.


Use Cases
----------

- As a user I want strategies to detect current and past problems and optimize
  the infrastructure accordingly.
- As a developer I want to make more effective strategies that can detect
  periodic patterns and make more informed decisions.
- As a developer I want to develop an external machine learning component to
  integrate with Watcher but still use already existing components of Watcher
  effectively.


Proposed change
===============

To enable time series the datasource base class will need a new method. This
method will allow metrics to be retrieved over a specific period with a
specific granularity. This method will return a list of values according to the
supplied parameters and will subsequently be implemented by all current
datasources. An example of how the interface of such a method could look is
shown below.

.. code-block:: python

  @abc.abstractmethod
  def statistic_series(self, resource, resource_type, meter_name, start_time,
                        end_time, granularity):
      """Retrieve metrics based on the specified parameters of a period of time

      :param resource: The object returned by clients such as Server or
      Hypersivor when calling nova.servers.get or nova.hypervisors.get
      :param resource_type: The Type of the resource object selected from
      RESOURCE_TYPES.
      :param start_time: The datetime to start retrieving metrics for
      :type start_time: datetime.datetime
      :param end_time: The datetime to limit the retrieval of metrics to
      :type end_time: datetime.datetime
      :param granularity: Interval between collected data in seconds.
      :return: Dictionary of key value pairs with timestamps and metric values
      """


In addition, a new class will be added that can utilize a datasource to perform
time series analysis. Features will include, decomposing trends, periodic
variations (daily, weekly, seasonal) and irregular variations (residuals). As
well as determining the stationarity. Any machine learning aspects such as
predicting future values through models like ARIMA will **not** be part of this
time series class.

A best effort should be made to find a lightweight library that implements the
desired time series functionality as libraries such as `numpy`_ or
`scikit-learn`_ are particularly large and offer substantially more
functionality than is required. If no suitable library can be found the
functionality will be implemented without the use of a third-party library.

.. _numpy: https://numpy.org/
.. _scikit-learn: https://scikit-learn.org/stable/index.html


Alternatives
------------

- The time series analysis along with any potential machine learning features
  could in its entirety be developed as an external service that integrates
  with Watcher. This would allow the use of libraries such as numpy and
  scikit-learn as they are very likely desired dependencies in a machine
  learning service. The time series method for datasources will still have to
  be implemented but the class for time series decomposition can be removed.


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

Collecting lists of values instead of single values per node and or instance
can significantly increase the memory consumption of Watcher. Especially, when
audits are run for large collections of nodes and instances. Additionally, the
transmission of all this data could potentially be a bottleneck if executed
sequentially. For this the time series class could utilize the `decision-engine
threadpool`_ to execute multiple requests in parallel.

.. _decision-engine threadpool: https://docs.openstack.org/watcher/latest/contributor/concurrency.html

Other deployer impact
---------------------

None


Developer impact
----------------

This change will expose a new method in datasources which could potentially be
used to enable machine learning features in external projects that integrate
with Watcher.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <dantalion>


Work Items
----------

- Introduce new method to datasource baseclass
- Implement new base method in all datasources
- Evaluate available lightweight time series libraries
- Implement simple time series class

Dependencies
============

* Potentially a new lightweight time series library will be added as
  dependency.


Testing
=======

- Unit tests for the new method such as validating the specified period
- Unit tests to verify the time series decompositions using known dummy data
- Unit tests to verify stationarity using known dummy data.
- Possible integration tests for testing the retrieval of time series metrics
  from datasources.

Documentation Impact
====================

No additional documentation is required apart from documenting newly
introduced methods and classes.


References
==========

- `decision-engine threadpool`_
- `numpy`_
- `scikit-learn`_


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Victoria
     - Introduced

