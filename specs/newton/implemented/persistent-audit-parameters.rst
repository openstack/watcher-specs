..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================================
Audit parameters should be persistent in Db
=====================================================

https://blueprints.launchpad.net/watcher/+spec/persistent-audit-parameters


Problem description
===================

When you start an audit, a new Audit object is created in Db with a reference
to an `Audit Template`_ object.

When processing an audit request, parameters taken into account by the
Watcher decision engine come from `Audit`_ object itself and also from
`Audit Template`_ ones (goal name, ...).

Problems:

If we update the `Audit Template`_ parameters or if we remove the
`Audit Template`_, we lose important information about the `Audit`_ itself.

What about data integrity for soft-deleted audit objects (useful for history) ?

If we introduce parameters for goals (as thresholds, ...) , we should be
able to update them. So how to keep persistent data for all audits
done to satisfy such configurable goals ?

How do we handle periodic audits when an audit template is updated ?

If we create an `Audit Template`_ with no strategy but with a `Goal`_ there
is a strategy selector that will automatically pick the most suited strategy
for the goal we specified (`watcher-strategy-selector`_) and since the
`Audit`_ has no record of which strategy was picked, we lose the information
stating the actual name of the strategy and the global efficacy is calculated
upon. Also, there can be a different strategy for an `Audit`_ simply because
the selection criteria changed over time (Ref. `blueprint efficacy indicator`_
and `watcher-strategy-selector`_). How do we persist strategy for an audit
for these cases ?

Other `Audit`_ impacting scenarios handled in different blueprints -

1. Impact on `Audit Template`_ and `Audit`_ when a `Goal`_ is deleted -
Addressed in blueprint `soft-delete-goals`_

2. Impact on `Audit Template`_ and `Audit`_ when a `Strategy`_ is deleted -
Addressed in blueprint `get-goal-from-strategy`_


Use Cases
----------
As an `Administrator`_
I need to ensure data integrity and consistency of an `Audit`_ when an
`Audit Template`_ is updated or removed.

As an `Administrator`_
I should be able to purge an`Audit Template`_ without impacting `Audit`_


Project Priority
-----------------
Essential for Newton-2

Proposed change
===============

* Modify audit schema to include strategy_id, goal_id and host_aggregate

Alternatives
------------
`Audit Template`_ to be immutable if there is any active `Audit`_ referencing
it. Any modifications to `Audit Template`_ should create a new record, so the
existing audits are not impacted.


Data model impact
-----------------
When an audit template is updated, an audit object should not lose related
data. We need to store goal_id and strategy_id in audit object. This ensures
data integrity for  `optimization-threshold`_ parameters
and strategy selections (Ref. `blueprint efficacy indicator`_ and
`watcher-strategy-selector`_)

Current audit structure::

  +-------------------+-------------+------+-----+---------+----------------+
  | Field             | Type        | Null | Key | Default | Extra          |
  +-------------------+-------------+------+-----+---------+----------------+
  | created_at        | datetime    | YES  |     | NULL    |                |
  | updated_at        | datetime    | YES  |     | NULL    |                |
  | deleted_at        | datetime    | YES  |     | NULL    |                |
  | deleted           | int(11)     | YES  |     | NULL    |                |
  | id                | int(11)     | NO   | PRI | NULL    | auto_increment |
  | uuid              | varchar(36) | YES  | UNI | NULL    |                |
  | type              | varchar(20) | YES  |     | NULL    |                |
  | state             | varchar(20) | YES  |     | NULL    |                |
  | deadline          | datetime    | YES  |     | NULL    |                |
  | audit_template_id | int(11)     | NO   | MUL | NULL    |                |
  +-------------------+-------------+------+-----+---------+----------------+

  +---------------------+--------------------------------------+
  | Property            | Value                                |
  +---------------------+--------------------------------------+
  | deadline            | None                                 |
  | type                | ONESHOT                              |
  | uuid                | ab49ee15-fa2b-4d3d-962f-01fe28b7fd92 |
  | audit_template_uuid | 7f1e48ba-2639-498e-8fff-9508cf706665 |
  +---------------------+--------------------------------------+

Proposed audit structure::

  +-------------------+-------------+------+-----+---------+----------------+
  | Field             | Type        | Null | Key | Default | Extra          |
  +-------------------+-------------+------+-----+---------+----------------+
  | created_at        | datetime    | YES  |     | NULL    |                |
  | updated_at        | datetime    | YES  |     | NULL    |                |
  | deleted_at        | datetime    | YES  |     | NULL    |                |
  | deleted           | int(11)     | YES  |     | NULL    |                |
  | id                | int(11)     | NO   | PRI | NULL    | auto_increment |
  | uuid              | varchar(36) | YES  | UNI | NULL    |                |
  | type              | varchar(20) | YES  |     | NULL    |                |
  | state             | varchar(20) | YES  |     | NULL    |                |
  | deadline          | datetime    | YES  |     | NULL    |                |
  | goal_id           | int(11)     | NO   | MUL | NULL    |                |
  | strategy_id       | int(11)     | YES  | MUL | NULL    |                |
  | host_aggregate    | int(11)     | YES  |     | NULL    |                |
  +-------------------+-------------+------+-----+---------+----------------+

  +---------------------+--------------------------------------+
  | Property            | Value                                |
  +---------------------+--------------------------------------+
  | deadline            | None                                 |
  | type                | ONESHOT                              |
  | uuid                | ab49ee15-fa2b-4d3d-962f-01fe28b7fd92 |
  | goal_uuid           | None                                 |
  | strategy_uuid       | None                                 |
  +---------------------+--------------------------------------+


REST API impact
---------------
Impacts following **audit** REST -

* GET /v1/audits
* GET /v1/audits/(audit_uuid)
* POST /v1/audits
* PATCH /v1/audits
* GET /v1/audits/detail

Security impact
---------------
None

Notifications impact
--------------------

None


Other end user impact
---------------------
Impacts openstack watcher command line:

The **python-watcherclient audit-create** should have options for
strategy-uuid, goal-uuid and host_aggregate while creating an audit

The **python-watcherclient audit-update** should include options for
updating strategy-uuid, goal-uuid and host_aggregate for an audit


Performance Impact
------------------

None

Other deployer impact
---------------------


Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:

Other Contributors:
hvprash
michaelgugino

Work Items
----------
* Update **Audit** object in **/watcher/db/sqlalchemy/models.py** to include
  strategy_id, goal_id and host_aggregate

* Synchronize audit_template and audit. Refactor the code to update
  strategy_id, goal_id and host_aggregate in both audit template and audit
  during CRUD operations. Following python files will be impacted:
  - ``/watcher/objects/audit_template.py``
  - ``/watcher/objects/audit.py``
  - ``/watcher/tests/api/v1/test_audit_templates.py``
  - ``/watcher/tests/api/v1/test_audits.py``
  - ``/watcher/tests/db/test_audit.py``
  - ``/watcher/tests/db/test_audit_template.py``

* Additional validation while soft deleting an audit template and purging.
  De-reference any **active audits** refering to an audit template:
  - ``/watcher/objects/audit_template.py``
  - ``/watcher/objects/audit.py``
  - ``/watcher/db/purge.py``

* Update unit tests and integration tests (Tempest scenarios)

* Changes to database migration script



Dependencies
============

None

Testing
=======


Documentation Impact
====================


References
==========

IRC discussions:


History
=======

None


.. _Administrator: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#administrator
.. _Goal: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#goal
.. _Audit Template: http://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit-template
.. _Audit: http://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit
.. _Strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Watcher Decision Engine: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-decision-engine
.. _Watcher database: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-database
.. _blueprint optimization-threshold: https://blueprints.launchpad.net/watcher/+spec/optimization-threshold
.. _watcher-strategy-selector: https://blueprints.launchpad.net/watcher/+spec/watcher-strategy-selector
.. _soft-delete-goals: https://blueprints.launchpad.net/watcher/+spec/soft-delete-goals
.. _get-goal-from-strategy: https://blueprints.launchpad.net/watcher/+spec/get-goal-from-strategy
.. _blueprint efficacy indicator: https://github.com/openstack/watcher-specs/blob/master/specs/newton/approved/efficacy-indicator.rst
.. _optimization-threshold: https://github.com/openstack/watcher-specs/blob/master/specs/mitaka/approved/optimization-threshold.rst
