..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================================
Supporting HA for background jobs in Watcher
============================================

https://blueprints.launchpad.net/watcher/+spec/background-jobs-ha

Problem description
===================

The main problem with the current implementation of the background scheduling
of jobs is if two or more decision-engine services are going to take
persisted jobs that are stored in DB then each DE service will take these jobs
twice or more.

There are no bindings like 'job <-> service' so main goal of this BP is
to provide a mechanism that will tag (route) jobs for DEs according to the
service instance they have associated with. Another future goal for this
feature would be to provide a job requeuing mechanism when the bound
'service_id' is marked as failed.

Use Cases
---------

As a Watcher administrator, I want to be sure that all Watcher services
using background jobs, which are working in HA-mode, will be synced with
scheduled jobs.

Proposed change
===============

`APScheduler`_ already has SQLAlchemyJobStore class that create table with
the following columns:

* id
* next_run_time
* job_state

Column 'job_state' contains dumped object of `Job`_. As we can see,
SQLAlchemyJobStore doesn't have relation between Decision Engine and its jobs.
I suggest to add new column 'service_id' that will be foreign key for
Service.id. This relation should entirely define relation between job and
service.
There also should be added new column 'tag' that will contain dict with
keys and values which will identify service uniquely. It usually is to contain
'host' and 'name' keys. Each type of job should then have its own tag so
we can easily perform some triaging/filtering on the list of jobs.

Alternatives
------------

None

Data model impact
-----------------

New table 'apscheduler_jobs' is to be added with the following columns:
* id
* next_run_time
* job_state
* service_id
* tag

REST API impact
---------------

None

Security impact
---------------

None

Notifications impact
--------------------

Since it is internal changes that shouldn't affect on user experience and
common workflow, no new notifications are expected.

Other end user impact
---------------------

'apscheduler_jobs' table should be included in new alembic version for the
Watcher DB.

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
  Alexander Chadin <alexchadin>

Work Items
----------

* Inherit new class from SQLAlchemyJobStore that will contain 'service_id'
  column and overwrite appropriate methods.
* Update watcher/decision_engine/audit/continuous.py to let it work with new
  job store.
* Implement appropriate unit tests to test various scenarios.


Dependencies
============

None expected

Testing
=======

Appropriate unit tests will be adapted to new changes.

Documentation Impact
====================

None

References
==========

https://blueprints.launchpad.net/watcher/+spec/background-jobs-ha

History
=======

No history

.. _Job: https://github.com/agronholm/apscheduler/blob/master/apscheduler/job.py#L230
.. _APScheduler: https://github.com/agronholm/apscheduler
