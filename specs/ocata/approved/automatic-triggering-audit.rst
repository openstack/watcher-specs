=============================================
Watcher automatic triggering audit
=============================================

https://blueprints.launchpad.net/watcher/+spec/automatic-triggering-audit


Problem description
===================

This blueprint goes beyond the "continuously-optimization" blueprint by
applying automatically the Action Plans.
https://blueprints.launchpad.net/watcher/+spec/continuously-optimization

Watcher needs to continuously optimize the OpenStack cloud for a specific
strategies or goals. Watcher can periodically trigger some Audit_ which
generates `Action Plan`_.

Unfortunately, in the current implementation the Administrator have to launch
manually the recommended Action Plan in order to apply it on the real system.

This specification relates to blueprint:
https://blueprints.launchpad.net/watcher/+spec/automatic-triggering-audit

Use Cases
---------

As administrator, telling audit to trigger the action plan everytime is a
a headache to the administator, so here we are implementing automatic
triggering functionality in audit which triggers the action plans.


Project Priority
----------------
Essential for Ocata-2


Proposed change
===============
The watcher system enables a private/public cloud administrator to launch
`Audit`_ on an Openstack cluster in order to optimize it in regards of one
or several goals.

We need to introduce new attribute in the AUDIT,
 - auto_trigger - To execute the action plans for the AUDIT.

An `Audit`_ is an optimization request but in case of
auto_trigger, when system finds auto_trigger=True
in the AUDIT, then it triggers the action plan for that audit.

The AutoTriggerActionPlan logic will be implemented under the
watcher/decision_engine/audit/base.py.

The AutoTriggerActionPlan class will contain all the logic related to trigger
the action plan for the audit. To trigger the action plan from
AutoTriggerActionPlan, we will use RPC call launch_action_plan.

At the a Applier level, currently only one action plan will execute.
https://github.com/openstack/watcher/blob/master/watcher/applier/manager.py#L30
If new action_plan is proposed while executing current action_plan, we will
cancel the new action by proper message "An action plan is currently running"
and the action plan state should also be set to SUPERSEDED.

Alternatives
------------

* To use a cronjob for audit which automatically triggers the action.

Data model impact
-----------------

* We need to introduce the new attribute in audit auto_trigger.

REST API impact
---------------

None expected

Security impact
---------------

We could have a security impact as the system could start running action plan
continuously and seriously damage the stability of the cluster.

Notifications impact
--------------------

None expected.

Other end user impact
---------------------

None expected

Performance Impact
------------------

No specific performance impact is expected.

Other deployer impact
---------------------

No specific deployer impact is envisaged.

Developer impact
----------------

This will not impact other developers working on OpenStack.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Alexander Chadin <alexchadin>
Other contributors:
  Digambar Patil <diga>
  Jean-Emile DARTOIS <jed56>

Work Items
----------

* Implement AutoTriggerActionPlanHandler class.
* Adapt API to support auto_trigger field as boolean.
* Add auto_trigger to audit in python-watcherclient.
* Add checkbox for auto_trigger in watcher-dashboard.
* Implement appropriate unit tests to test various scenarios.

Dependencies
============

None expected

Testing
=======

Appropriate unit tests will be adapted to new changes.

Documentation Impact
====================

It will be necessary to add new content relating to this change.

References
==========

https://blueprints.launchpad.net/watcher/+spec/continuously-optimization

History
=======

No history.

.. _APScheduler: https://github.com/agronholm/apscheduler
.. _Strategies: http://docs.openstack.org/developer/watcher/glossary.html#strategy
.. _Administrator: http://docs.openstack.org/developer/watcher/glossary.html#administrator
.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit
.. _Action Plan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _Cluster: http://docs.openstack.org/developer/watcher/glossary.html#cluster
.. _BackgroundScheduler: https://github.com/agronholm/apscheduler/blob/master/examples/schedulers/background.py
.. _API source file: https://github.com/openstack/watcher/blob/master/watcher/api/controllers/v1/audit.py
.. _watcher-notifications-ovo: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
