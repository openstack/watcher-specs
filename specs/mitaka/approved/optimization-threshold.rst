..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================
Optimization Threshold
======================

https://blueprints.launchpad.net/watcher/+spec/optimization-threshold

Allow decision engine to pass strategy parameters, like optimization threshold,
to selected strategy, also strategy to provide parameters info to end user.


Problem description
===================

Currently all parameters used in strategy are hard coded, end users can't
modify them unless they change the source code. E.g. THRESHOLD of strategy
outlet_temp_control is critical and fixed as 35.0, so we can't tune it for
specific usage case without changing source code.

Use Cases
----------

As an administrator.
I can choose a goal to optimize my cluster and Watcher will show me a list of
custom parameters for the selected strategy.

As an operator.
I want to tune the strategy parameter in an easy way for my cloud. I wish I can
change it via watcher command line to achieve the best solution.

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

Need following to enable strategy parameter:

* Add more info into audit-template, so that 'watcher audit-template-show'
  tells end user selected strategy and its parameters. Also append these info
  to the 'watcher audit-template-create' output.
* Add new cmd option '-p' to 'watcher audit-create' for strategy parameter
  configuration. End user can specify all strategy parameters, like
  "-p threshold=45.0 -p repeat=10".
* When 'watcher audit-create', decison engine would configure selected strategy
  with these parameters before executing it.

Alternatives
------------

None

Data model impact
-----------------

For audit template, need add info of selected strategy and its parameters. For
audit, need store user specified strategy parameters by hashmap.

The audit template structure is as follows::

  +----------------+-------------------------------------------+
  | Property       | Value                                     |
  +----------------+-------------------------------------------+
  | goal           | DUMMY                                     |
  | strategy       | outlet_temp_control                       |
  | parameter_info | {'threshold': (float, 'Temperature ...')} |
  | description    | None                                      |
  | name           | 1th_template                              |
  | host_aggregate | None                                      |
  | uuid           | 0c49a52c-4a0f-4dea-9e19-471360823aef      |
  +----------------+-------------------------------------------+

The audit structure is as follows::

  +---------------------+--------------------------------------+
  | Property            | Value                                |
  +---------------------+--------------------------------------+
  | uuid                | b564665b-e77b-444c-a43f-3ae654b9a551 |
  | audit_template_name | 1st_template                         |
  | parameters          | {'threshold': 35.0}                  |
  | created_at          | 2016-01-31T08:51:03+00:00            |
  | updated_at          | 2016-01-31T08:51:58+00:00            |
  | audit_template_uuid | 06cdba2a-069b-4618-8948-540854d8d911 |
  | state               | SUCCEEDED                            |
  | deadline            | None                                 |
  | deleted_at          | None                                 |
  | type                | ONESHOT                              |
  +---------------------+--------------------------------------+


REST API impact
---------------

Audit creation API: POST /v1/audit
is changed, so that extra strategy parameters hashmap is accepted in request
body.

E.g. to create one audit based on outlet_temperature template with required
parameters, we can just POST following::

  {
      "type": "ONESHOT",
      "audit_template_uuid": "outlet_temperature_template",
      "parameters": {
          "threshold": 35.0,
          "repeat": 10
      }
  }


Security impact
---------------

Strategy parameter controls the executing process, and odd parameter probably
leads unexpected behavior. This BP enables easy changing of parameter, thus
need check against input parameter to make sure it is in reasonable range.


Notifications impact
--------------------

None

Other end user impact
---------------------

python-watcherclient need add extra command line for parameter input. End user
needs to be aware of this for strategy parameter tuning.

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
  edwin-zhai


Work Items
----------

* Refactor the code to move strategy selection from audit creation to
  audit-template creation. As we have no strategy parameter info until
  instantiate it.

* Extend the audit-template to show the info of selected strategy and related
  parameters

* Add extra command line in python-watcherclient, so that strategy parameter
  can be specified with 'watcher audit-create -p xxx=XXX -p yyy=YYY ...'

* When 'watcher audit-create', parameter should be used to configure the
  selected strategy after validation, where voluptuous can be used just like
  action parameter checking.

* Update Horizon plugin for watcher to make sure it still works with these
  changes.

* Each strategy class with parameter need define a new function,
  'input_parameters', to set all parameters, e.g. threshold.

* Each strategy calss with parameter need define a new function,
  'parameters_info', to return parameter info, like 'name', 'type' and
  'description'.


Dependencies
============

None


Testing
=======

Adds unit and functional test for strategy parameter.


Documentation Impact
====================

Need update the watcher API doc and user guide. In dev doc about strategy
implementation, need explain how to add input parameters for strategy.

References
==========

None


History
=======

None
