..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================================
Purge soft-deleted Watcher objects
==================================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/db-purge-engine

Watcher never deletes data from its DBs and only uses soft deletion (There
is special column in each table indicating whether or not an entry is
deleted). We keep these data for potential future ML processing in order to
improve Watcher auditing recommendations. However, we shall provide a purge
mechanism to Cloud Administrator_ in order to limit the size of this
database_ and make sure it does not increase too much.


Problem description
===================

As of now, Watcher does not provide anything to facilitate the removal of soft
deleted objects. So the only way to destroy objects into the Watcher database
is to connect directly onto the database backend server and to execute DB
commands (or script) to remove objects in tables. Moreover, some objects can
be linked (e.g. a set of Action_ objects are linked to a same `Action Plan`_
object, the latter being linked to a unique Audit_ object). Remove manually
such objects can create orphan (e.g. an Action oject with no more linked
Action Plan object) in the database. Finally, you could introduce
inconsistencies into the database by removing a subset of objects having
a same parent (e.g. remove half of action objects linked to a same action plan
object will break this action plan integrity).

Watcher database size is not unlimited and queries performance can be degraded
due to a huge quantity of soft-deleted objects remained into the  Db storage.

Finally, usage of soft-deleted objects is not clearly defined today.


Use Cases
----------

As a Cloud Administrator_, I want to manage the size of the Watcher database by
purging all soft-deleted objects.

As a Cloud Administrator, I should be able to purge a subset of the Watcher
objects from the database by providing a validity interval as an argument (in
days) which shall not be destroyed. (e.g. I want to delete objects older than
30 days).

As a Cloud Administrator, I should be able to purge all objects linked to a
particular `Audit Template`_, by providing, as argument, the Audit Template
UUID.

As a Cloud Administrator, I would like to be notified about the number of
objects to be deleted (this number should be computed by Watcher), before
validating or not this purge operation.

As a Cloud Administrator, I would like to get, as result, a detailed summary
of the purge operation (i.e. the total number of deleted objects, the number
of deleted Audit Templates, the number of deleted Audits_, the number of
deleted `Action Plans`_, the number of deleted Actions_).

As a Developer, when an Audit template object is removed, all linked Audit
objects shall be removed.

As a Developer, when an Audit object is removed, all linked Action plans
objects shall be removed.

As a Developer, when an Action Plan object is removed, all linked Actions
objects should be removed.

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

Add an option to watcher-db-manage command tool to be able to purge the Watcher
database.

Alternatives
------------

Do nothing and let operators handle this on their own.

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

The watcher-db-manage command is only available to administrator. Obviously any
entry point to deleting data permanently is dangerous but this spec assumes the
deployer has taken the necessary security precautions to lock down access to
the watcher-db-manage command already.


Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

There could be some impact when doing a large purge, so as part of the command
implementation there will be a --max-number option. Note that the object
integrity must be respected: We shall not remove a part of objects associated
in the same parent object. For example, removing of the half of Actions_
recommended by an `Action Plan`_ (because we reach the max number of purged
object) does not make any sense, and the integrity of this action plan will be
violated.

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
  None

Work Items
----------
* Update DBCommand_ class by adding new option 'purge'
* Implement purge feature
* Update 'Watcher Manual Pages' documentation


Dependencies
============

A lot of OpenStack projects already propose purge mechanism. It would be
pertinent to have a look on their mechanism implementation, if needed.

* glance : https://review.openstack.org/#/c/216782/
* cinder : https://review.openstack.org/#/c/146766/
* nova : https://review.openstack.org/#/c/203751/
* ospurge : https://github.com/openstack/ospurge

Testing
=======

Add these functional tests :

* I purge all objects marked as DELETED.
* I purge all objects marked as DELETED, in a maximum limit of M objects.
* I purge all objects marked as DELETED and linked to a dedicated Audit
  Template
* I purge all objects marked as DELETED and linked to a dedicated Audit
  Template, in a maximum limit of M objects.
* I purge all objects marked as DELETED and older than N days.
* I purge all objects marked as DELETED and older than N days, in a maximum
  limit of M objects.
* I purge all objects marked as DELETED, older than N days and linked to
  a dedicated Audit Template.
* I purge all objects marked as DELETED, older than N days and linked to
  a dedicated Audit Template, in a maximum limit of M objects.

For all of these tests, we should be able to validate integrity of remaining
objects (no orphans, no partial group of objects linked to a same parent).

Documentation Impact
====================

Add a new page into 'Watcher Manual Pages'.

References
==========

None


History
=======

None


.. _Action: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action
.. _Actions: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action
.. _Audit: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit
.. _Audits: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit
.. _Action Plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Action Plans: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Administrator: http://factory.b-com.com/www/watcher/doc/watcher/glossary.html#administrator
.. _Audit Template: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit-template
.. _database: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-database
.. _DbCommand: https://github.com/openstack/watcher/blob/master/watcher/cmd/dbmanage.py#L33
