..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===============================
Enhance Watcher Applier Engine
===============================

https://blueprints.launchpad.net/watcher/+spec/enhance-watcher-applier-engine

`Taskflow`_ is the default workflow engine for Watcher Applier.
In Watcher the flow pattern for linked actions is Graph flow.
For parent action A and child action B, this means B depends on A
and that the execution of B must wait until A finished.
Taskflow has a callback function to decide at runtime whether B
should be allowed to execute. The callback function returns
a boolean True to allow B execution or False to not.
Currently the callback function always returns True in Watcher Applier.


Problem description
===================

For example, we want to live migrate a VM, if there are two potential
target nodes that meet the requirements. However, we don't know which
one will definitely be able to migrate successfully. The existing
strategy will select one to create a Migrate action and the action may
fail if there are no enough resource in the destination node.
A solution is that we can make two linked actions for the two
potential targets. If first action succeeded, then the second action
will be ignored. Otherwise continue to execute the second one.
For this purpose, We need the callback function returns True or False
depending on the result of previous action A execution.
Action B should be executed unless action A failed. If action A
executes success, the execution of action B should be ignored.

Use Cases
----------

As a Watcher user, I want to decide an action whether to be executed
depending on the result of a previous action.


Proposed change
===============

Now the callback function, named decider, always returns True. We propose
to add a new config option 'action_execution_rule' which is a dict type.
Its key field is strategy name and the value is 'ALWAYS' or 'ANY'.
'ALWAYS' means the callback function returns True as usual.
'ANY' means the return depends on the result of previous action execution.
The callback returns True if previous action gets failed, and the engine
continues to run the next action. If previous action executes success,
the callback returns False then the next action will be ignored.
For strategies that aren't in 'action_execution_rule', the callback always
returns True.

If exception is throwing out during the action execution, reverting will
be triggered by taskflow. To continue executing the next action,
we return False instead of throwing an exception.

Alternatives
------------

None

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

The default value of 'action_execution_rule' doesn't change
the behavior of Applier.

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

* Add a new config option 'action_execution_rule'
* Implement the callback function


Dependencies
============

None


Testing
=======

Unittest for all changes


Documentation Impact
====================

None


References
==========

None


History
=======

None

.. _Taskflow: https://docs.openstack.org/taskflow/latest/
