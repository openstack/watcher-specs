..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
General purpose decision engine threadpool
==========================================

https://blueprints.launchpad.net/watcher/+spec/general-purpose-decision-engine-threadpool

Many I/O operations such as writing to disk or waiting for network responses
take a long amount of time. By leveraging parallelism the time taken to
perform such operations can be drastically reduced. The general purpose
threadpool for the decision engine will allow to perform methods in parallel,
thereby reducing the time required to perform these operations.

Problem description
===================

The general purpose threadpool will reduce the time it takes to perform certain
operations of the decision engine. Currently, the gathering of metrics or the
building of the data model can take large amounts of time proportionally for
example.

Use Cases
----------

- As a user I want the execution of an audit to be performed as quickly as
  possible.

Proposed change
===============

Introduce a general purpose threadpool using the `futurist`_ library for which
end users can configure the amount of threads. This will introduce a new class
that uses a singular pattern so it can be used throughout the decision engine.
The threadpool will use the GreenThreadPoolExecutor as it does not conflict
with other threadpools used in the decision engine. The singleton will contain
several methods to simplify the submission of tasks and waiting for their
completion.

.. _futurist: https://docs.openstack.org/futurist/latest/

With the threadpool the building of the data model will be parallelized which
is done in three steps. First the calls to retrieve information about
aggregates and availability zones are executed in parallel. The information is
used to submit tasks to gather the information about each compute node.
Finally, using `futures`_ will allow to immediately submit a task to retrieve
the information about instances for a given compute node.

.. _futures: https://docs.python.org/dev/library/concurrent.futures.html

Alternatives
------------

A purpose build threadpool specific for building the data model. However, this
would mean that introducing parallelism in other parts of the decision engine
would again require the design and implementation of yet another threadpool.

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

Overall the time take to perform audits should significantly decrease, however,
a large amount of threads could negatively impact external services. Because of
this the default amount of threads should be a relatively safe value for most
OpenStack infrastructures.

Other deployer impact
---------------------

Deployers should evaluate the amount of threads they want Watcher to use based
on the scale of their infrastructure.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <dantalion>

Work Items
----------

- Implement the threadpool singleton based on previous proof of concepts.

- Modify the method to build the data model to use the three step parallelism
  as described.

- Implement relevant test cases to test the threadpool and the building of the
  data model.

Dependencies
============

* futurist, A library maintained and developed by OpenStack.


Testing
=======

Both the behavior of the building of the data model as well as the threadpool
should be evaluated.

- The verifying of behavior for helper methods in the threadpool.

- The verifying of the completeness of the data model when build with
  parallelization.

Documentation Impact
====================

The documentation will be updated to include usage examples that indicate to
other developers how to best use the threadpool. Additionally, typical use
cases in what situations this threadpool will be most useful will be provided.


References
==========

* `futurist`_
* `futures`_

.. _futurist: https://docs.openstack.org/futurist/latest/
.. _futures: https://docs.python.org/dev/library/concurrent.futures.html

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Ussuri
     - Introduced

