..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================
Cron-based continuous audits
============================

https://blueprints.launchpad.net/watcher/+spec/cron-based-continuous-audits

Problem description
===================

Watcher currently implements a user specified interval when running continuous
audits. This may cause some collisions when the Watcher services are down,
because the next audit time isn't stored in the database.
Using a time interval isn't a flexible or user-friendly solution, instead,
we should use an industry standard like cron syntax that provides an elastic
way to schedule and execute an audit.

Use Cases
---------

* As an administrator, I want to use cron syntax to schedule audit execute.

* As an administrator, I want be sure that Watcher will set up next time
  executing of audits properly.

Proposed change
===============

Watcher API already has 'interval' property in Audit object so we can use it to
store cron like format. API is to check type of incoming interval and if it is
string type then Watcher uses `croniter`_ module to set next run time.
The second proposition is to provide persistence for current 'interval' column.
To do it, we need to properly update next_run_time since its value may be less
than current time. In this case, we may use the following algorithm:

::

    delta = timedelta(seconds=
        (interval - (current_time-old_next_run_time).seconds % interval))
    next_run_time = current_time + delta

For example, Watcher had to run audit at 7:30 am, but services went down and we
have restored it only at 9:00 am. Using interval with 3600 value, Watcher has
to set next run time at 9:30 am.

To make this spec, we need to be sure that Watcher can store continuous jobs
and its services, which may work in HA mode, takes only tag-assigned jobs.
Blueprint background-jobs-ha takes responsibility to implement job store
mechanism.

Alternatives
------------

* Continue to use already provided interval.

* Delete continuous audits after each maintenance mode and create new ones.

Data model impact
-----------------

* Type of interval column of Audit table should be changed to string type.

* New column next_run_time has to be added to Audit table.

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

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Alexander Chadin <alexchadin>

Work Items
----------

* Add next_run_time column to Audit table.
* Use croniter module to support cron-like syntax in Watcher.
* Update python-watcherclient to support cron-like syntax.
* Add logic to calculate values for next_run_time field.

Dependencies
============

https://blueprints.launchpad.net/watcher/+spec/continuously-optimization
https://blueprints.launchpad.net/watcher/+spec/background-jobs-ha

Testing
=======

Unit tests should be updated.

Documentation Impact
====================

Update documentation to mention cron and interval.

References
==========

None

History
=======

None

.. _croniter: https://pypi.python.org/pypi/croniter