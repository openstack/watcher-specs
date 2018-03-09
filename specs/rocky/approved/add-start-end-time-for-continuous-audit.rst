..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===============================================
Add the start and end time for CONTINUOUS audit
===============================================

https://blueprints.launchpad.net/watcher/+spec/add-start-end-time-for-continuous-audit

Currently we can only set audit execution interval, but we can not set audit start and end time.
We need to add the audit start and end time for CONTINUOUS audit.


Problem description
===================

For CONTINUOUS audit, it will run periodically after launch.
There is no way to control the start and end time of CONTINUOUS audit yet.

Use Cases
----------

As a Watcher user, I want to set the start and end time for CONTINUOUS audit.


Proposed change
===============

* Add new start_time and end_time fields in the audit table
* For CONTINUOUS audit, if its state is PENDING or ONGOING, launch the audit
  only if the current time is between start_time and end_time

The user can specify the start and end time or any one, If user doesn't specify start and end time,
the audit's behavior is the same as before. If no start time, audit starts after creating.
If no end time, audit runs until its state is SUSPENDED or CANCELLED.
If end time is provided, the audit will be set from ONGOING to SUCCEEDED
after end time and not running again.
The datetime format is ISO 8601, such as: YYYY-MM-DD hh:mm:ss

Here are some CLI examples:

create audit with start and end time:

.. code:: bash

   $ watcher audit create -g dummy -t CONTINUOUS -i 300 \
     --start-time '2018-04-01 08:00:00' --end-time '2018-04-03 08:00:00'

update audit start or end time:

.. code:: bash

   $ watcher audit update 64aa6c03-b676-4904-9d6a-855d1d6f9200 \
     replace start_time='2018-04-02 20:30:00'

   $ watcher audit update 64aa6c03-b676-4904-9d6a-855d1d6f9200 \
     replace end_time='2018-04-04 20:30:00'

Alternatives
------------

May reuse 'interval' field instead of the new start_time and end_time fields.
But it will cause complication and not easy to understand.

Data model impact
-----------------

Add new start_time and end_time fields in the audit table

REST API impact
---------------

Need to add new 'start_time' and 'end_time' parameters in Audits APIs.
Their values are local time.

Security impact
---------------

None

Notifications impact
--------------------

Add 'start_time' and 'end_time' to AuditPayload

Other end user impact
---------------------

* Need to add 'start_time' and 'end_time' to CLI 'watcher audit create'
* Also need to update watcher-dashboard

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
  licanwei

Work Items
----------

* Update architecture doc to add the new fields
* Add new start_time and end_time fields in the audit table
* Check start and end time before running CONTINUOUS audit
* Update notification AuditPayload
* Update python-watcherclient
* Update watcher-dashboard


Dependencies
============

None


Testing
=======

Unittest for all changes


Documentation Impact
====================

Update architecture doc to add the new fields.


References
==========

None


History
=======

None
